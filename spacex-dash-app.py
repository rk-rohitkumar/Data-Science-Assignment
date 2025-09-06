import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash app
app = dash.Dash(__name__)

# Create dropdown options for launch sites plus "All Sites"
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    html.Br(),

    # Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Payload range slider
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload,
                    step=1000,
                    marks={int(i): f'{int(i)}' for i in range(int(min_payload), int(max_payload)+1, 5000)},
                    value=[min_payload, max_payload]),
    
    # Scatter plot for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for updating pie chart based on selected launch site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value'))
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Count of success for all sites
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(success_counts, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # For a specific launch site show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['Outcome', 'Count']
        outcome_counts['Outcome'] = outcome_counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(outcome_counts, values='Count', names='Outcome',
                     title=f'Success vs Failure for Site {selected_site}')
    return fig

# Callback for scatter plot correlated with selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')])
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                                (spacex_df['Payload Mass (kg)'] <= high)]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                (spacex_df['Payload Mass (kg)'] >= low) &
                                (spacex_df['Payload Mass (kg)'] <= high)]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version',
                     title='Payload vs Launch Outcome',
                     labels={'class': 'Launch Success (1=Success, 0=Failure)'},
                     hover_data=['Launch Site'])
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
