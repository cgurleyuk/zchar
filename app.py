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

st.title("gm/Id Methodology Visualization")

st.markdown("""
This tool helps visualize the **gm/Id methodology**. It interfaces with IHP SG13G2 models using ngspice to run DC sweeps for a given set of MOS parameters.
""")

with st.sidebar:
    st.header("Device Parameters")
    # specific device names
    device_name = st.selectbox("Device Type", [
        "sg13_lv_nmos", 
        "sg13_lv_pmos", 
        "sg13_hv_nmos", 
        "sg13_hv_pmos"
    ])
    
    st.subheader("Dimensions")
    col1, col2 = st.columns(2)
    # W and L in microns
    width = col1.number_input("Width (um)", value=10.0, step=1.0)
    length = col2.number_input("Length (um)", value=1.0, step=0.1)
    
    col3, col4 = st.columns(2)
    ng = col3.number_input("Fingers (ng)", value=1, step=1, min_value=1)
    m = col4.number_input("Multiplier (m)", value=1, step=1, min_value=1)
    
    st.subheader("Biasing")
    vgs_max = st.number_input("Max Vgs (V)", value=1.2, step=0.1)
    vds = st.number_input("Vds (V)", value=0.9, step=0.1)
    vbs_val = st.number_input("Vbs (V)", value=0.0, step=0.1)
    
    run_btn = st.button("Run Simulation", type="primary")

if run_btn:
    with st.spinner("Running Simulation with ngspice..."):
        # Run Simulation
        try:
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
                st.success("Simulation Complete!")
                
                # Generate plots
                # Effective width = width_instance * m
                # ng splits width, so width_instance is total width of that instance.
                figs = create_plots(df, width * 1e-6 * int(m), length * 1e-6)
                
                # Layout plots using 2x2 grid
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(figs[0], use_container_width=True) # gm/Id vs Id/W
                    st.plotly_chart(figs[2], use_container_width=True) # ft vs gm/Id
                
                with col2:
                    st.plotly_chart(figs[1], use_container_width=True) # gm/gds vs gm/Id
                    st.plotly_chart(figs[3], use_container_width=True) # Id vs Vgs

                # Show raw data (expandable using full dataframe)
                with st.expander("View Raw Data"):
                    st.dataframe(df)
                    
            else:
                st.error("Simulation returned no data. Check ngspice output.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
