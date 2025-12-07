import subprocess
import os
import tempfile
import uuid
import shutil
from pathlib import Path
from .templates import NMOS_SWEEP_TEMPLATE, PMOS_SWEEP_TEMPLATE
from .parser import parse_ngspice_data

def run_dc_sweep(
    device_name: str,
    width: float,
    length: float,
    vds: float,
    vgs_max: float,
    vgs_step: float = 0.01,
    vbs: float = 0.0,
    ng: int = 1,
    m: int = 1,
    model_path: str = None,
    sim_config: dict = None
):
    """
    Runs a DC sweep for the given device parameters.
    Returns a pandas DataFrame with results.
    """
    
    # Default config values if not provided (fallback)
    pdk_root = "/home/cgurleyuk/analog/pdk/IHP-Open-PDK"
    pdk_code = "ihp-sg13g2"
    ngspice_bin = "ngspice"

    if sim_config:
        pdk_root = sim_config.get("pdk_root", pdk_root)
        pdk_code = sim_config.get("pdk_code", pdk_code)
        # Expand user path for ngspice if provided
        if "ngspice_path" in sim_config:
            ngspice_bin = os.path.expanduser(sim_config["ngspice_path"])
    
    # Verify ngspice executable exists if it's an absolute path, 
    # otherwise trust it's in PATH or handle failure later.
    if os.path.isabs(ngspice_bin) and not os.path.exists(ngspice_bin):
        # Fallback or error? For now, we'll try to proceed or just let subprocess fail.
        # But we can try system ngspice if custom fails.
        if shutil.which("ngspice"):
             ngspice_bin = "ngspice"

    run_id = str(uuid.uuid4())
    # Use local directory to avoid potential temp permission/path issues with ngspice
    work_dir = Path.cwd() / ".sim_buffer"
    work_dir.mkdir(exist_ok=True)
    
    sim_dir = work_dir / run_id
    sim_dir.mkdir(parents=True, exist_ok=True)
    
    netlist_file = sim_dir / "input.cir"
    output_file = sim_dir / "output.txt"
    
    # Env variables for spiceinit
    env = os.environ.copy()
    env["PDK_ROOT"] = pdk_root
    env["PDK"] = pdk_code
    
    # Model configuration
    # We rely on .spiceinit 'sourcepath' to find the library files
    # so we just need the filename.
    if "hv" in device_name.lower():
        lib_filename = "cornerMOShv.lib"
    else:
        lib_filename = "cornerMOSlv.lib" 

    # Determine polarity and template
    if "nmos" in device_name.lower():
        template = NMOS_SWEEP_TEMPLATE
    else:
        template = PMOS_SWEEP_TEMPLATE

    # Format netlist
    # Note: we don't pass full path for model_path anymore, just the lib name 
    # because spiceinit handles the search path.
    netlist_content = template.format(
        model_path=lib_filename,
        model_name=device_name,
        width=width,
        length=length,
        ng=ng,
        m=m,
        vds=vds,
        vgs_max=vgs_max,
        vgs_step=vgs_step,
        vbs=vbs,
        output_file=str(output_file)
    )
    
    with open(netlist_file, "w") as f:
        f.write(netlist_content)
        
    # Final check before running
    if not shutil.which(ngspice_bin) and not (os.path.isfile(ngspice_bin) and os.access(ngspice_bin, os.X_OK)):
        if sim_config and "ngspice_path" in sim_config:
             raise FileNotFoundError(f"Ngspice executable not found at configured path: '{sim_config['ngspice_path']}' (expanded: '{ngspice_bin}') and not in system PATH.")
        else:
             raise FileNotFoundError(f"Ngspice not found in system PATH and no 'ngspice_path' configured.")

    try:
        # Run ngspice from the CURRENT directory so it finds .spiceinit
        # We pass the absolute path to netlist_file
        cmd = [ngspice_bin, "-b", str(netlist_file)]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            env=env, # Pass env with PDK paths
            cwd=os.getcwd() # Explicitly run from project root
        )
        
        # Parse results
        if not output_file.exists():
            print(f"Error: Output file not produced.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            return None
            
        # Parse output
        try:
            return parse_ngspice_data(str(output_file), device_name)
        except Exception as e:
            print(f"Error reading simulation output: {e}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"NGSPICE Execution Failed:\n{e.stdout}\n{e.stderr}")
        return None
    finally:
        # Cleanup
        # shutil.rmtree(sim_dir) # Keep for debugging if needed, or implement cleanup
        if sim_dir.exists():
            shutil.rmtree(sim_dir)
