# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                    {'label': 'All Sites', 'value': 'ALL'}] + [
                    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
                ],
                 value='ALL',
                 placeholder="Select a Launch Site Here",
                 searchable=True),

    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['class'] = counts['class'].map({1: 'Success', 0: 'Failure'})

        fig = px.pie(
            counts,
            values='count',
            names='class',
            title=f'Success vs Failure for {selected_site}'
        )
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, selected_payload_range):
    low, high = selected_payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation Between Payload and Success for All Sites'
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation Between Payload and Success for {selected_site}'
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
