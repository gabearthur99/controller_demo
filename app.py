import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sub
import dash
import sim_funcs

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
server = app.server

## Global Constants
COLOR = '#d9d9d9'
STATE_LAYOUT = dict(plot_bgcolor='white',
                xaxis=dict(title='Time [sec]',
                         linecolor=COLOR,
                         showgrid=True,
                         gridcolor = COLOR,
                         zeroline=True,
                         zerolinecolor=COLOR),
                yaxis=dict(title='State',
                         linecolor=COLOR,
                         showgrid=True,
                         gridcolor=COLOR,
                         zeroline=True,
                         zerolinecolor=COLOR),
                showlegend=True
)

PHASE_LAYOUT = dict(plot_bgcolor='white',
                xaxis=dict(title='Theta [rad]',
                         linecolor=COLOR,
                         showgrid=True,
                         gridcolor = COLOR,
                         zeroline=True,
                         zerolinecolor=COLOR),
                yaxis=dict(title='Theta_dot [rad/s]',
                         linecolor=COLOR,
                         showgrid=True,
                         gridcolor=COLOR,
                         zeroline=True,
                         zerolinecolor=COLOR),
                showlegend=False,
                width = 1200,
                height = 850
)

def get_default_fig(layout):
    fig = go.Figure()
    fig.update_layout(layout)
    return fig

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                html.H2("Spacecraft Controller Demo"),
                html.H5("By Gabe Arthur"),
            ], width=True),
        ], align="end"),
        dcc.Graph(figure = get_default_fig(STATE_LAYOUT), id='state_graph', animate=True),
            dbc.Row([dbc.Col([html.Div("Theta_0"),
                        dcc.Input(
                        id="input-t0",
                        type='number',
                        value=0.5,
                        step=0.1,
                        placeholder="Theta_0",),
                        html.Div("Theta_dot_0"),
                        dcc.Input(
                        id="input-td0",
                        type='number',
                        value=0,
                        step=0.1,
                        placeholder="Theta_0",),
                        html.Div("Moment of Inertia"),
                        dcc.Input(
                        id="input-I",
                        type='number',
                        value=1,
                        step=0.1,
                        placeholder="I",)],width=3),

                        dbc.Col([html.Div("Kp"),
                        dcc.Input(
                        id="input-Kp",
                        type='number',
                        value=-1,
                        step=0.1,
                        placeholder="Kp",),
                        html.Div("Kd"), dcc.Input(
                        id="input-Kd",
                        type='number',
                        value=-1,
                        step=0.1,
                        placeholder="Kd",),
                        html.Div("Umax"), dcc.Input(
                        id="input-umax",
                        type='number',
                        value=1,
                        min=0,
                        step=0.1,
                        placeholder="Umax",),
                        ], width=3),

                        dbc.Col([html.Div("Select Controller Type"),
                        dcc.Dropdown(['PD', 'bang_bang'], 'PD', id='controller-dropdown'),
                        html.Div("tf"), dcc.Input(
                        id="input-tf",
                        type='number',
                        value=20,
                        step=1,
                        placeholder="tf",),
                        ], width=3),
                    
                    dbc.Col(html.Button('Run Simulation', id='run-button', n_clicks=0),width=3),
                    dbc.Col(html.Button('Generate Phase Portrait', id='gen-phase', n_clicks=0), width=3)
  
            ]),
            dcc.Graph(figure = get_default_fig(PHASE_LAYOUT), id='phase_graph', animate=True)
    ]
)


@app.callback(Output(component_id='state_graph', component_property='figure'), 
                Input(component_id='run-button', component_property='n_clicks'),
                State(component_id='input-Kp', component_property='value'),
                State(component_id='input-Kd', component_property='value'),
                State(component_id='input-t0', component_property='value'),
                State(component_id='input-td0', component_property='value'),
                State(component_id='input-I', component_property='value'),
                State(component_id='input-umax', component_property='value'),
                State(component_id='controller-dropdown', component_property='value'),
                State(component_id='input-tf', component_property='value'),
                prevent_initiall_callback=True
                )
def update_state_plot(n_clicks, Kp, Kd, theta0, thetadot0, I, Umax, controlLaw, tf):
    [time, X, U] = sim_funcs.run_sim(controlLaw, Umax, Kp, Kd, I, theta0, thetadot0, tf, True)
    fig = get_default_fig(STATE_LAYOUT)
    fig.add_trace(go.Scatter(
    x = time,
    y = X[:, 0],
    mode = 'lines+markers',
    name = 'Theta [rad]')
    )
    fig.add_trace(go.Scatter(
        x = time,
        y = X[:, 1],
        mode = 'lines+markers',
        name = 'Theta_dot [rad/sec]')
    )
    fig.add_trace(go.Scatter(
        x = time,
        y = U,
        mode = 'lines+markers',
        name = 'U [Nm]')
    )
    if not (Umax == np.inf):
        fig.add_trace(go.Scatter(
            x = time,
            y = [Umax]*len(time),
            mode = 'lines',
            name = 'U_max [Nm]',
            legendrank = 1)
        )
        fig.add_trace(go.Scatter(
            x = time,
            y = [-Umax]*len(time),
            mode = 'lines',
            name = 'U_min [Nm]',
            legendrank = 1)
        )
    
    return fig



@app.callback(Output(component_id='phase_graph', component_property='figure'), 
                Input(component_id='gen-phase', component_property='n_clicks'),
                State(component_id='input-Kp', component_property='value'),
                State(component_id='input-Kd', component_property='value'),
                State(component_id='input-t0', component_property='value'),
                State(component_id='input-td0', component_property='value'),
                State(component_id='input-I', component_property='value'),
                State(component_id='input-umax', component_property='value'),
                State(component_id='controller-dropdown', component_property='value'),
                State(component_id='input-tf', component_property='value'),
                prevent_initiall_callback=True
                )
def update_phase_plot(n_clicks, Kp, Kd, theta0, thetadot0, I, Umax, controlLaw, tf):
    # Generate Phase Data
    theta_min = -np.pi
    theta_max = np.pi
    theta_dot_min = -1
    theta_dot_max = 1
    Nx = 5
    [theta0s,thetadot0s]= sim_funcs.gen_X0s(theta_min, theta_max, theta_dot_min, theta_dot_max, Nx)
    phase_data = sim_funcs.gen_phase_data(controlLaw, Umax, Kp, Kd, I, theta0s, thetadot0s, tf)

    # Init Output Plot
    fig = get_default_fig(PHASE_LAYOUT)

    # Populate Phase Portrait
    for i in range(len(theta0s)):
        for j in range(len(thetadot0s)):
            X = [phase_data[i, j]][0]
            # Add the trace
            fig.add_trace(go.Scatter(
            x = X[:,0],
            y = X[:, 1],
            mode = 'lines+markers')
            )

    for i in range(len(theta0s)):
        for j in range(len(thetadot0s)):
            # Add the starting point
            fig.add_trace(go.Scatter(
                          x = [theta0s[i]],
                          y = [thetadot0s[j]],
                          marker=dict(
                                     color='black',
                                     size=10
                                     )
                          )

            )

    return fig


app.title = "Spacecraft Controller Demo"
app.run_server(debug=False, port=8080)

## TODO: Can't figure out why the legend lables are not showing up in LaTex