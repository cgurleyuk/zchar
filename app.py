import streamlit as st
import os
import sys
import json
from simulation.runner import run_dc_sweep
from plotting.charts import create_plots
import config_utils

# Page configuration
st.set_page_config(
    page_title="zchar: gm/Id Visualization Tool",
    page_icon="⚡",
    layout="wide"
)

# st.title("gm/Id Methodology Visualization")

# st.markdown("""
# This tool helps visualize the **gm/Id methodology**. It interfaces with IHP SG13G2 models using ngspice to run DC sweeps for a given set of MOS parameters.
# """)

with st.sidebar:
    st.header("device parameters")
    
    # Load configuration
    config, error_msg = config_utils.load_process_config()
    
    if error_msg:
        st.error(error_msg)
    
    if config:
        devices = list(config['devices'].keys())
        device_name = st.selectbox("device type", devices)
        
        # Get limits for selected device
        limits = config['devices'][device_name]
        min_w, max_w = limits['min_width'], limits['max_width']
        min_l, max_l = limits['min_length'], limits['max_length']
        max_vgs_limit = limits['max_vgs']
    else:
        # Fallback if config fails
        device_name = st.selectbox("device type", ["sg13_lv_nmos"])
        min_w, max_w = 1.0, 100.0
        min_l, max_l = 0.13, 10.0
        max_vgs_limit = 1.8

    st.subheader("dimensions")
    col1, col2 = st.columns(2)
    
    # Helper to clamp values in session state to avoid errors
    def clamp_val(key, min_v, max_v, default):
        if key in st.session_state:
            val = st.session_state[key]
            if val < min_v: st.session_state[key] = min_v
            if val > max_v: st.session_state[key] = max_v
        return default

    # Width limit logic:
    # W_total = W_finger * ng
    # Constraint: min_w_finger <= W_finger <= max_w_finger
    # Therefore: min_w_finger * ng <= W_total <= max_w_finger * ng
    
    # Get current ng from session state or default to 1
    # We need to look ahead at what 'ng' is, or use default for first run.
    # Since 'ng' widget is below, we rely on session state availability.
    current_ng = st.session_state.get('ng', 1)
    
    eff_min_w = min_w * current_ng
    eff_max_w = max_w * current_ng
    
    # W and L in microns
    # Ensure default values are within new limits
    default_w = clamp_val('width', eff_min_w, eff_max_w, 10.0)
    # If default 10.0 is out of range, clamp it too for the 'value' arg
    default_w = max(eff_min_w, min(default_w, eff_max_w))
    
    width = col1.number_input("width (um)", min_value=eff_min_w, max_value=eff_max_w, value=default_w, step=1.0, key="width")
    
    default_l = clamp_val('length', min_l, max_l, 0.13)
    default_l = max(min_l, min(default_l, max_l))
    length = col2.number_input("length (um)", min_value=min_l, max_value=max_l, value=default_l, step=0.5, key="length")
    
    col3, col4 = st.columns(2)
    ng = col3.number_input("fingers (ng)", value=1, step=1, min_value=1, key="ng")
    m = col4.number_input("multiplier (m)", value=1, step=1, min_value=1, key="m")
    
    st.subheader("biasing")
    default_vgs = clamp_val('vgs_max', 0.0, max_vgs_limit, max_vgs_limit) # Default to max
    default_vgs = max(0.0, min(default_vgs, max_vgs_limit))
    vgs_max = st.number_input("max vgs (v)", min_value=0.0, max_value=max_vgs_limit, value=default_vgs, step=0.1, key="vgs_max")
    
    vds = st.number_input("vds (v)", value=0.9, step=0.1, key="vds")
    vbs_val = st.number_input("vbs (v)", value=0.0, step=0.1, key="vbs_val")
    
    # Initialize Session State
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'last_params' not in st.session_state:
        st.session_state.last_params = {}

    run_on_change = st.checkbox("autorun", value=False)
    
    col_hist1, col_hist2 = st.columns([1, 1], vertical_alignment="center")
    with col_hist1:
        show_history = st.checkbox("show previous", value=True)
    with col_hist2:
        history_depth = st.number_input("max", min_value=1, max_value=10, value=1, step=1)
    
    run_btn = st.button("run", type="primary")

    # Current parameters (to detect change)
    current_params = {
        'device_name': device_name,
        'width': width,
        'length': length,
        'ng': ng,
        'm': m,
        'vgs_max': vgs_max,
        'vds': vds,
        'vbs': vbs_val
    }

    # Check validity of change
    params_changed = current_params != st.session_state.last_params

    should_run = False
    if run_btn:
        should_run = True
    elif run_on_change and params_changed:
        should_run = True

    if should_run:
        with st.spinner("running simulation with ngspice..."):
            try:
                # Store current data in history before updating
                if st.session_state.data is not None:
                    # Append current data AND params to history
                    # We store as a dict to keep them together
                    result_entry = {
                        'data': st.session_state.data.copy(),
                        'params': st.session_state.last_params.copy()
                    }
                    st.session_state.history.append(result_entry)
                    
                    # Trim history to configured depth
                    if len(st.session_state.history) > history_depth:
                        st.session_state.history = st.session_state.history[-history_depth:]

                # Run Simulation
                # inputs are in microns, runner expects meters
                df = run_dc_sweep(
                    device_name=device_name,
                    width=width * 1e-6, 
                    length=length * 1e-6,
                    vds=vds,
                    vgs_max=vgs_max,
                    vbs=vbs_val,
                    ng=int(ng),
                    m=int(m),
                    sim_config=config # Pass the full config object
                )
                
                if df is not None and not df.empty:
                    st.session_state.data = df
                    st.session_state.last_params = current_params.copy()
                else:
                    st.error("simulation returned no data. check ngspice output.")
                    
            except Exception as e:
                st.error(f"an error occurred: {str(e)}")

# Always generate plots
# If data is None, create_plots will return empty figures
# Prepare history list based on toggle
history_to_plot = st.session_state.history if show_history else []

# Bundle current data with its params
current_result = None
if st.session_state.data is not None:
    current_result = {
        'data': st.session_state.data,
        'params': st.session_state.last_params
    }

figs = create_plots(
    current=current_result,
    history=history_to_plot
)

# Layout plots using 2x2 grid
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(figs[0], use_container_width=True) # gm/Id vs Id/W
    st.plotly_chart(figs[2], use_container_width=True) # ft vs gm/Id

with col2:
    st.plotly_chart(figs[1], use_container_width=True) # gm/gds vs gm/Id
    st.plotly_chart(figs[3], use_container_width=True) # Id vs Vgs