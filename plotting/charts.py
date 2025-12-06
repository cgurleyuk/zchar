import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_plots(df: pd.DataFrame, width: float, length: float):
    """
    Generates a list of plotly figures for standard gm/Id plots.
    """
    
    # Pre-calculate derived metrics
    w_over_l = width / length if length > 0 else 1.0
    
    # Ensure positive Id for log plots
    # Note: we use copies to avoid modifying the original DF view in the app if it matters, 
    # but here we are just calculating columns.
    df['id_abs'] = df['id'].abs()
    df['id_norm'] = df['id_abs'] / w_over_l
    df['ft_ghz'] = df['ft'] / 1e9
    
    # 1. gm/Id vs Normalized Current (Id / (W/L))
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['id_norm'], 
        y=df['gm_id'],
        mode='lines',
        name='gm/Id'
    ))
    fig1.update_layout(
        title="Efficiency (gm/Id) vs Current Density (Id / (W/L))",
        xaxis_title="Id / (W/L) [A]",
        yaxis_title="gm/Id [V^-1]",
        xaxis_type="log",
        xaxis=dict(showgrid=True, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridcolor='LightGray'),
        template="plotly_white"
    )
    
    # 2. Intrinsic Gain (gm/gds) vs gm/Id
    # Linear Y axis as requested.
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['gm_id'], 
        y=df['gm_gds'],
        mode='lines',
        name='Gain'
    ))
    fig2.update_layout(
        title="Intrinsic Gain (gm/gds) vs gm/Id",
        xaxis_title="gm/Id [V^-1]",
        yaxis_title="Intrinsic Gain [V/V]",
        # yaxis_type="log", # Removed for Linear Scale
        xaxis=dict(autorange="reversed", showgrid=True, gridcolor='LightGray'),
        template="plotly_white"
    )

    # 3. Transit Frequency (ft) vs gm/Id
    # GHz units.
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df['gm_id'], 
        y=df['ft_ghz'],
        mode='lines',
        name='ft'
    ))
    fig3.update_layout(
        title="Transit Frequency (ft) vs gm/Id",
        xaxis_title="gm/Id [V^-1]",
        yaxis_title="ft [GHz]",
        yaxis_type="log",
        xaxis=dict(autorange="reversed", showgrid=True, gridcolor='LightGray'),
        template="plotly_white"
    )
    
    # 4. Id vs Vgs
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df['vgs'].abs(), 
        y=df['id_abs'],
        mode='lines',
        name='Id'
    ))
    fig4.update_layout(
        title="Drain Current vs Vgs",
        xaxis_title="|Vgs| [V]",
        yaxis_title="|Id| [A]",
        yaxis_type="log",
        template="plotly_white"
    )
    
    return [fig1, fig2, fig3, fig4]
