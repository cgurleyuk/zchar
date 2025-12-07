import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_plots(df: pd.DataFrame | None, width: float, length: float, df_prev: pd.DataFrame | None = None):
    """
    Generates a list of plotly figures for standard gm/Id plots.
    If df is None, returns empty plots with correct axes.
    If df_prev is provided, overlays it as dashed lines.
    """
    
    # 1. gm/Id vs Normalized Current (Id / (W/L))
    fig1 = go.Figure()
    
    # 2. Intrinsic Gain (gm/gds) vs gm/Id
    fig2 = go.Figure()

    # 3. Transit Frequency (ft) vs gm/Id
    fig3 = go.Figure()
    
    # 4. Id vs Vgs
    fig4 = go.Figure()

    figs = [fig1, fig2, fig3, fig4]

    # Helper to add traces
    def add_data_traces(dataframe, are_previous=False):
        if dataframe is None or dataframe.empty:
            return

        # Pre-calculate derived metrics locally
        # We recalculate here to be safe, assuming raw spice output columns exist
        w_over_l = width / length if length > 0 else 1.0
        
        # Avoid SettingWithCopyWarning if valid DF
        d = dataframe.copy()
        d['id_abs'] = d['id'].abs()
        d['id_norm'] = d['id_abs'] / w_over_l
        d['ft_ghz'] = d['ft'] / 1e9

        line_props = dict(dash='dash', color='gray') if are_previous else dict()
        suffix = " (Prev)" if are_previous else ""
        opacity = 0.6 if are_previous else 1.0

        # 1. gm/Id vs Id/W
        fig1.add_trace(go.Scatter(
            x=d['id_norm'], 
            y=d['gm_id'],
            mode='lines',
            name=f'gm/Id{suffix}',
            line=line_props,
            opacity=opacity
        ))

        # 2. gm/gds vs gm/Id
        fig2.add_trace(go.Scatter(
            x=d['gm_id'], 
            y=d['gm_gds'],
            mode='lines',
            name=f'Gain{suffix}',
            line=line_props,
            opacity=opacity
        ))

        # 3. ft vs gm/Id
        fig3.add_trace(go.Scatter(
            x=d['gm_id'], 
            y=d['ft_ghz'],
            mode='lines',
            name=f'ft{suffix}',
            line=line_props,
            opacity=opacity
        ))

        # 4. Id vs Vgs
        fig4.add_trace(go.Scatter(
            x=d['vgs'].abs(), 
            y=d['id_abs'],
            mode='lines',
            name=f'Id{suffix}',
            line=line_props,
            opacity=opacity
        ))

    # Add previous data first (so it's behind current data)
    add_data_traces(df_prev, are_previous=True)
    # Add current data
    add_data_traces(df, are_previous=False)

    # Update Layouts (Common settings)
    fig1.update_layout(
        title="efficiency (gm/Id) vs current density (Id / (W/L))",
        xaxis_title="Id / (W/L) [A]",
        yaxis_title="gm/Id [V^-1]",
        xaxis_type="log",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        template="plotly_white"
    )
    
    fig2.update_layout(
        title="intrinsic gain (gm/gds) vs gm/Id",
        xaxis_title="gm/Id [V^-1]",
        yaxis_title="gm/gds [V/V]",
        xaxis=dict(autorange="reversed", showgrid=True),
        template="plotly_white"
    )

    fig3.update_layout(
        title="transit frequency (ft) vs gm/Id",
        xaxis_title="gm/Id [V^-1]",
        yaxis_title="ft [GHz]",
        xaxis=dict(autorange="reversed", showgrid=True),
        template="plotly_white"
    )
    
    fig4.update_layout(
        title="drain current vs Vgs",
        xaxis_title="|Vgs| [V]",
        yaxis_title="|Id| [A]",
        yaxis_type="log",
        xaxis=dict(showgrid=True),
        template="plotly_white"
    )
    
    return figs
