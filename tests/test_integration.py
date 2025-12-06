
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.runner import run_dc_sweep

def test_integration():
    print("Testing NMOS Sweep...")
    df = run_dc_sweep(
        device_name="sg13_lv_nmos",
        width=10e-6,
        length=1e-6,
        vds=0.9,
        vgs_max=1.8,
        ng=1,
        m=1
    )
    
    if df is not None:
        print("Success! Data Shape:", df.shape)
        print("Columns:", df.columns)
        print(df.head())
        # Check if derived columns exist
        if 'gm_id' in df.columns:
            print("Derived columns present.")
    else:
        print("Simulation FAILED.")

    print("-" * 30)

    print("Testing PMOS Sweep...")
    df_p = run_dc_sweep(
        device_name="sg13_lv_pmos",
        width=10e-6,
        length=1e-6,
        vds=0.9,
        vgs_max=1.8,
        ng=1,
        m=1
    )
    if df_p is not None:
         print("Success PMOS! Data Shape:", df_p.shape)
    
    print("-" * 30)

    print("Testing HV NMOS Sweep...")
    df_hv_n = run_dc_sweep(
        device_name="sg13_hv_nmos",
        width=10e-6,
        length=1e-6,
        vds=3.3,
        vgs_max=3.3,
        ng=1,
        m=1
    )
    if df_hv_n is not None:
        print("Success HV NMOS! Data Shape:", df_hv_n.shape)
        
    print("-" * 30)
    
    print("Testing HV PMOS Sweep...")
    df_hv_p = run_dc_sweep(
        device_name="sg13_hv_pmos",
        width=10e-6,
        length=1e-6,
        vds=3.3,
        vgs_max=3.3,
        ng=1,
        m=1
    )
    if df_hv_p is not None:
        print("Success HV PMOS! Data Shape:", df_hv_p.shape)

if __name__ == "__main__":
    test_integration()
