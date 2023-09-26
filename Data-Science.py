import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc

# Load data
df = pd.read_csv('ChicagoCensusData.csv')
df = df[df['HARDSHIP_INDEX'].notna()]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define layout
app.layout = dbc.Container([
    dbc.Row([dbc.Col(html.H1("Chicago Census Data Dashboard", className='text-center text-primary, mb-4'), width=12)]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="select_variable", options=[{"label": x, "value": x} for x in df.columns[2:]], multi=False, value='PERCENT_OF_HOUSING_CROWDED', style={'width': "40%"}),
            html.Div(id='output_container', children=[]),
            dcc.Graph(id='my_chicago_map', figure={}),
            dcc.Graph(id='my_histogram', figure={}),
            dcc.Graph(id='my_bar_chart', figure={}),
            dcc.Graph(id='my_box_plot', figure={}),
        ], width=6),

        dbc.Col([
            dcc.Graph(id='my_heatmap', figure={}),
            dcc.Graph(id='my_pie_chart', figure={}),
            html.H2("Summary Statistics", className='text-center text-primary, mb-4'),
            dash_table.DataTable(id='summary_table', columns=[{"name": i, "id": i} for i in df.describe().columns], data=df.describe().to_dict('records'),),
            html.H2("Top 5 Community Areas by Per Capita Income", className='text-center text-primary, mb-4'),
            dash_table.DataTable(id='income_table', columns=[{"name": i, "id": i} for i in df.nlargest(5, 'PER_CAPITA_INCOME').columns], data=df.nlargest(5, 'PER_CAPITA_INCOME').to_dict('records'),),
            html.H2("Top 5 Community Areas by Hardship Index", className='text-center text-primary, mb-4'),
            dash_table.DataTable(id='hardship_table', columns=[{"name": i, "id": i} for i in df.nlargest(5, 'HARDSHIP_INDEX').columns], data=df.nlargest(5, 'HARDSHIP_INDEX').to_dict('records'),),
        ], width=6),
    ])
])

# Define callback function
@app.callback(
    [Output('output_container', 'children'),
     Output('my_chicago_map', 'figure'),
     Output('my_histogram', 'figure'),
     Output('my_heatmap', 'figure'),
     Output('my_bar_chart', 'figure'),
     Output('my_pie_chart', 'figure'),
     Output('my_box_plot', 'figure')],
    [Input('select_variable', 'value')]
)
def update_graph(option_slctd):
    container = f"The variable chosen by user was: {option_slctd}"
    dff = df.copy()
    
    scatter_fig = px.scatter(dff, x="PER_CAPITA_INCOME", y=option_slctd, size="HARDSHIP_INDEX", color="COMMUNITY_AREA_NAME", hover_name="COMMUNITY_AREA_NAME", log_x=True, size_max=60)
    histogram_fig = px.histogram(dff, x=option_slctd)

    numeric_columns = dff.select_dtypes(include=['float64', 'int64']).columns
    heatmap_fig = ff.create_annotated_heatmap(z=dff[numeric_columns].corr().values, x=list(dff[numeric_columns].corr().columns), y=list(dff[numeric_columns].corr().index), annotation_text=dff[numeric_columns].corr().round(2).values, showscale=True)

    bar_chart_fig = px.bar(dff, x="COMMUNITY_AREA_NAME", y="PER_CAPITA_INCOME")
    pie_chart_fig = px.pie(dff, names="HARDSHIP_INDEX")
    box_plot_fig = px.box(dff, x="COMMUNITY_AREA_NAME", y="PER_CAPITA_INCOME")

    return container, scatter_fig, histogram_fig, heatmap_fig, bar_chart_fig, pie_chart_fig, box_plot_fig

if __name__ == '__main__':
    app.run_server(debug=True)
