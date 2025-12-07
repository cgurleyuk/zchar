import pandas as pd
import numpy as np

def parse_ngspice_data(file_path: str, device_name: str) -> pd.DataFrame:
    """
    Parses the whitespace-separated output file from ngspice.
    Returns a pandas DataFrame.
    """
    try:
        # ngspice wrdata format:
        # col1 col2 col3 col4 ...
        # We need to skip header if present (wrdata usually doesn't have a header line unless specified?)
        # wrdata output example:
        # 0.000000e+00 6.542201e-09 0.000000e+00 1.797203e-03 ...
        
        # We might need to handle column names if 'wrdata' puts them there?
        # Usually wrdata is just numbers.
        
        df_raw = pd.read_csv(file_path, sep=r'\s+', header=None)
    except Exception as e:
        print(f"Error parsing csv: {e}")
        return pd.DataFrame() # Return empty on error
        
    if df_raw.empty:
        return pd.DataFrame()

    # We take col 0 as Vgs (or Vsg for PMOS potentially, though our sweep is Vgs)
    
    # Map raw columns to meaningful names
    # New format: ids gm gds cgg
    # wrdata produces X Y pairs
    # Col 0: Vgs
    # Col 1: ids
    # Col 2: Vgs
    # Col 3: gm
    # ...
    
    id_col = 1
    gm_col = 3
    gds_col = 5
    cgg_col = 7
    
    data = pd.DataFrame()
    data['vgs'] = df_raw.iloc[:, 0]
    
    # Process Id
    # Model 'ids' parameter is always positive magnitude of channel current
    data['id'] = df_raw.iloc[:, id_col].abs()
    data['id'] = data['id'].apply(lambda x: max(x, 1e-15)) 

    # Process gm (directly from model)
    data['gm'] = df_raw.iloc[:, gm_col]
    
    # Process gds (directly from model)
    data['gds'] = df_raw.iloc[:, gds_col]
    
    # Process cgg (directly from model)
    data['cgg'] = df_raw.iloc[:, cgg_col]
    
    
    # Calculate gm/Id
    data['gm_id'] = data.apply(lambda row: row['gm'] / row['id'] if abs(row['id']) > 1e-18 else 0, axis=1)
    
    # Intrinsic Gain: gm/gds
    data['gm_gds'] = data.apply(lambda row: row['gm'] / row['gds'] if abs(row['gds']) > 1e-18 else 0, axis=1)
    
    # Transit Frequency ft ~ gm / (2 pi Cgg)
    # Cgg is total gate capacitance. cgg output is typically capacitance (positive or negative depending on spice?)
    # Usually cgg is positive total gate cap.
    data['ft'] = data.apply(lambda row: row['gm'] / (2 * np.pi * abs(row['cgg'])) if abs(row['cgg']) > 1e-18 else 0, axis=1)
    
    return data
