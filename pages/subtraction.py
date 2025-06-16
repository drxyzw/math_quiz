import dash
from dash import html, dcc
dash.register_page(__name__, path="/subtraction/")
layout = html.Div([
    html.H1("Subtraction")
])
