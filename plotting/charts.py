import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_plots(df: pd.DataFrame | None, width: float, length: float, dfs_prev: list[pd.DataFrame] | None = None):
    """
    Generates a list of plotly figures for standard gm/Id plots.
    If df is None, returns empty plots with correct axes.
    If dfs_prev is provided (list of DFs), overlays them as dashed lines.
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
    def add_data_traces(dataframe, is_previous=False, index=0):
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

        if is_previous:
            line_props = dict(dash='dash', color='gray')
            # 1-based index for the legend: "Prev #1" is the most recent previous result
            suffix = f" (prev #{index})"
            opacity = 0.5
        else:
            line_props = dict(color='red') # user requested consistent red for current
            suffix = ""
            opacity = 1.0

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
    if dfs_prev:
        # Assuming dfs_prev is ordered oldest to newest. 
        # We want "Prev #1" to be the most recent history item (last in the list).
        # "Prev #2" is the one before that.
        total_prev = len(dfs_prev)
        for i, df_p in enumerate(dfs_prev):
             # Logic for label index:
             # if i=0 (oldest), loop index=0. If total=3.
             # We want label to be #3.
             # if i=2 (newest), we want label to be #1.
             # label_idx = total_prev - i
             label_idx = total_prev - i
             add_data_traces(df_p, is_previous=True, index=label_idx)

    # Add current data
    add_data_traces(df, is_previous=False)

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
