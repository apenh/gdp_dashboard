from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import math
import os
sys.path.append(os.getcwd())
import plotly.express as px
from IPython import embed
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import seaborn as sns
import numpy as np
import git
import plotly.graph_objects as go
from bayesian.td_tool.runBayesCsc_2 import Bayesian_Inference
from bayesian.td_tool.bayes_csc import getTime, getDrift
from bayesian.td_tool.td_lib import getVel
#from pages._3_Checkshot_Data import get_data, filter_data

df_sonic_2 = st.session_state['Sonic_log']
df_checkshot_2 = st.session_state['Checkshot']
df_checkshot = df_checkshot_2
df_sonic = df_sonic_2

if df_sonic.empty:
    st.write("No sonic log available.")
    exit(0)
#raw_cks_df, df_checkshot, df_sonic = get_data()
#wells = raw_cks_df.uwi.unique().tolist()

uwi = st.session_state['uwi']
#df_checkshot, df_sonic, df_merged = filter_data(df_checkshot, df_sonic, raw_cks_df, uwi)
st.write(f'Well Selected: {uwi}')
st.write('You can either run the bayesian inference with Standard values or select some of the parameters yourself.')
clas = Bayesian_Inference()
df_well, td_z, td_t, ww, water_depth, water_velocity = clas.run(df_checkshot, df_sonic, uwi)
well_z = df_well['TVDMSL'].values
well_vp_ext = df_well['VP_EXT'].values
well_vp = df_well['VP_BAYES'].values

td_vp = getVel(td_z, td_t)

td_df = pd.DataFrame({'depth':td_z,'twt':td_t,'vp':td_vp})
td_df = td_df.dropna()
td_z = td_df['depth'].values
td_t = td_df['twt'].values
td_vp = td_df['vp'].values


well_t_ext = getTime(well_z, well_vp_ext)
well_t = getTime(well_z, well_vp)
td_drift_t_ext, td_drift_z_ext, well_drift_t_ext, well_drift_z_ext = getDrift(td_z, td_t, well_z, well_t_ext)    
td_drift_t, td_drift_z, well_drift_t, well_drift_z = getDrift(td_z, td_t, well_z, well_t)    

fig = go.Figure()

#, "VELOCITY DIFFERENCE", "TWT", "DRIFT (OWT)", "VELOCITY BAYESIAN"]

fig = make_subplots(rows=1, cols=5, subplot_titles=["VELOCITY","VELOCITY DIFFERENCE","TIME","DRIFT","VELOCITY BAYESIAN"])

yr = [np.max(np.union1d(well_z, td_z)) * 1.1, 0]
# Subplot 1: Velocity
fig.add_trace(go.Scatter(x=well_vp_ext, y=well_z, mode='lines', name='Vp Prior', line=dict(color='green'), legendgroup="1"), row=1, col=1)
fig.add_trace(go.Line(x=td_vp, y=td_z, line_shape='hv',line=dict(color='red'), legendgroup="1", name='Vp Checkshot'), row=1, col=1)
fig.add_trace(go.Scatter(x=[-1e4, 1e4], y=[water_depth, water_depth], mode='lines',line=dict(color='black', dash='dash'), name='Seabed', legendgroup="1"), row=1, col=1)
fig.update_yaxes(title_text="Y-axis 1", row=1, col=1, autorange='reversed')
fig.update_xaxes(title_text="yaxis 2 title", range=[0, np.max(np.union1d(well_vp, td_vp)) * 1.2], row=1, col=1)
#fig.update_layout(showlegend=True, row =1, col=1)

# Subplot 2: Velocity Difference
xx = well_vp - well_vp_ext
fig.add_trace(go.Scatter(x=xx, y=well_z, mode='lines', line=dict(color='blue'), name="Vp Prior - Vp Posterior", legendgroup="2"), row=1, col=2)
xmin = np.min(xx) - 10
xmax = np.max(xx) + 10
fig.add_trace(go.Scatter(x=[-1e4, 1e4], y=[water_depth, water_depth], mode='lines',line=dict(color='black', dash='dash'), legendgroup="2", showlegend=False), row=1, col=2)
fig.update_yaxes(row=1, col=2, autorange='reversed', range=[0,yr])
fig.update_xaxes(title_text="yaxis 2 title", range=[xmin, xmax], row=1, col=2)
fig.add_vline(x=0, line_width=1, line_color="black", row=1, col=2)


# Subplot 3: Time Plot
fig.add_trace(go.Line(x=1e3 * well_t_ext, y=well_z, line=dict(color='green'), legendgroup="3", name='TWT Prior'), row=1, col=3)
fig.add_trace(go.Line(x=1e3 * well_t, y=well_z, line=dict(color='blue'), legendgroup="3", name='TWT Posterior'), row=1, col=3)
fig.add_trace(go.Scatter(x=1e3 * td_t, y=td_z, mode='markers', line=dict(color='red'), legendgroup="3", name='TWT Checkshot'), row=1, col=3)
fig.add_trace(go.Scatter(x=[-1e4, 1e4], y=[water_depth, water_depth], mode='lines',line=dict(color='black', dash='dash'), legendgroup="3", showlegend=False), row=1, col=3)
fig.update_yaxes(row=1, col=3,autorange='reversed', range=[0,yr])
fig.update_xaxes(title_text='ms', range=[-100, np.max(1e3 * well_t) * 1.1], row=1, col=3)

# Subplot 4: DRIFT Plot
fig.add_trace(go.Line(x=1e3 * td_drift_t_ext, y=td_z, line=dict(color='green'), legendgroup="4", name='Drift Prior'), row=1, col=4)
fig.add_trace(go.Line(x=1e3 * td_drift_t, y=td_z, line=dict(color='blue'), legendgroup="4", name='Drift Posterior'), row=1, col=4)
xx = np.insert(well_drift_t, 0, well_drift_t_ext)
xx = xx[~np.isnan(xx)]
fig.add_trace(go.Scatter(x=[-1e4, 1e4], y=[water_depth, water_depth], mode='lines',line=dict(color='black', dash='dash'), legendgroup="4", showlegend=False), row=1, col=4)
fig.update_yaxes(title_text="Y-axis 1", row=1, col=4, autorange='reversed', range=[0,yr])
fig.update_xaxes(title_text="DRIFT (OWT)", range=[1e3 * np.min(xx) - 3, 1e3 * np.max(xx) + 3], row=1, col=4)
fig.add_vline(x=0, line_width=1, line_color="black", row=1, col=4)

# Subplot 5: Velocity Bayesian Plot
fig.add_trace(go.Scatter(x=well_vp, y=well_z, mode='lines', name='Vp Posterior', line=dict(color='blue'), legendgroup="5"), row=1, col=5)
fig.add_trace(go.Line(x=td_vp, y=td_z, line_shape='hv',line=dict(color='red'), legendgroup="5",name='Vp Checkshot'), row=1, col=5)
fig.add_trace(go.Scatter(x=[-1e4, 1e4], y=[water_depth, water_depth], mode='lines',line=dict(color='black', dash='dash'), legendgroup="5", showlegend=False), row=1, col=5)
fig.update_yaxes(title_text="Y-axis 1", row=1, col=5, autorange='reversed', range=[0,yr])
fig.update_xaxes(title_text="yaxis 2 title", range=[0, np.max(np.union1d(well_vp, td_vp)) * 1.2], row=1, col=5)
fig.update_layout(width=1600, height=1200,legend=dict(orientation="h",xanchor = "center",x = 0.5),legend_tracegroupgap=300)


st.plotly_chart(fig)