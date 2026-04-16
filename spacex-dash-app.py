import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")

max_payload = spacex_df['PayloadMass'].max()
min_payload = spacex_df['PayloadMass'].min()

app = dash.Dash(__name__)

site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['LaunchSite'].unique()
]

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(id='site-dropdown', options=site_options, value='ALL',
                 placeholder='Select a Launch Site here', searchable=True),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter to successful launches only, then count per site
        success_df = spacex_df[spacex_df['Class'] == 1]
        site_counts = success_df.groupby('LaunchSite').size().reset_index(name='count')
        fig = px.pie(site_counts, values='count', names='LaunchSite',
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['LaunchSite'] == entered_site]
        outcome_counts = filtered_df['Class'].value_counts().reset_index()
        outcome_counts.columns = ['Class', 'count']
        outcome_counts['outcome'] = outcome_counts['Class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(outcome_counts, values='count', names='outcome',
                     title=f'Success vs. Failure for site: {entered_site}')
    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['PayloadMass'] >= low) &
                            (spacex_df['PayloadMass'] <= high)]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['LaunchSite'] == entered_site]
        title = f'Payload vs. Outcome for site: {entered_site}'
    else:
        title = 'Payload vs. Outcome for All Sites'
    fig = px.scatter(filtered_df, x='PayloadMass', y='Class',
                     color='BoosterVersion', title=title,
                     labels={'Class': 'Launch Outcome (1=Success, 0=Failure)'})
    return fig

if __name__ == '__main__':
    app.run()
