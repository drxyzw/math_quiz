import dash
from dash import html, dcc
dash.register_page(__name__, path="/division/")
layout = html.Div([
    html.H1("Division")
])
