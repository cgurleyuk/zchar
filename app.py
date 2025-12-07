import streamlit as st
import os
import sys
from simulation.runner import run_dc_sweep
from plotting.charts import create_plots

# Page configuration
st.set_page_config(
    page_title="gm/Id Visualization Tool",
    page_icon="⚡",
    layout="wide"
)

# st.title("gm/Id Methodology Visualization")

# st.markdown("""
# This tool helps visualize the **gm/Id methodology**. It interfaces with IHP SG13G2 models using ngspice to run DC sweeps for a given set of MOS parameters.
# """)

with st.sidebar:
    st.header("device parameters")
    # specific device names
    device_name = st.selectbox("device type", [
        "sg13_lv_nmos", 
        "sg13_lv_pmos", 
        "sg13_hv_nmos", 
        "sg13_hv_pmos"
    ])
    
    st.subheader("dimensions")
    col1, col2 = st.columns(2)
    # W and L in microns
    width = col1.number_input("width (um)", value=10.0, step=1.0)
    length = col2.number_input("length (um)", value=0.13, step=0.1)
    
    col3, col4 = st.columns(2)
    ng = col3.number_input("fingers (ng)", value=1, step=1, min_value=1)
    m = col4.number_input("multiplier (m)", value=1, step=1, min_value=1)
    
    st.subheader("biasing")
    vgs_max = st.number_input("max vgs (v)", value=1.8, step=0.1)
    vds = st.number_input("vds (v)", value=0.9, step=0.1)
    vbs_val = st.number_input("vbs (v)", value=0.0, step=0.1)
    
    # Initialize Session State
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'prev_data' not in st.session_state:
        st.session_state.prev_data = None
    if 'last_params' not in st.session_state:
        st.session_state.last_params = {}

    run_on_change = st.checkbox("autorun", value=False)
    run_btn = st.button("run simulation", type="primary")

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
                # Store current data as previous before updating
                if st.session_state.data is not None:
                    st.session_state.prev_data = st.session_state.data.copy()

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
                    m=int(m)
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
figs = create_plots(
    st.session_state.data, 
    width * 1e-6 * int(m), 
    length * 1e-6,
    df_prev=st.session_state.prev_data
)

# Layout plots using 2x2 grid
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(figs[0], use_container_width=True) # gm/Id vs Id/W
    st.plotly_chart(figs[2], use_container_width=True) # ft vs gm/Id

with col2:
    st.plotly_chart(figs[1], use_container_width=True) # gm/gds vs gm/Id
    st.plotly_chart(figs[3], use_container_width=True) # Id vs Vgs