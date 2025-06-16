import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import random

dash.register_page(__name__, path="/addition/")

HEADER_STYLE = {
    "backgroundColor": "#f8f9fa",  # optional: light gray background
    # "padding": "2rem 1rem",
}

CONTENT_STYLE = {
    "padding": "2rem 1rem",
}

levels = ["Elemtary (1-digit and no regrouping)",
                    "Easy (1-digit and regrouping)",
                    "Intermediate (2-digit)",
                    ]
content = html.Div([
    dbc.Button("Start", id="button-start", size="lg", n_clicks=0, className="w-100"),
    html.Br(), html.Br(),  # adds line breaks
    dcc.RadioItems(id="level",
                   options=levels,
                    value=levels[0]),
    dcc.Store(id="store-answer"),
    dcc.Store(id="store-finished-count", data=0),
    dcc.Store(id="store-correct-count", data=0),
    dcc.Store(id="store-incorrect-count", data=0),
    dcc.Store(id="store-current-time", data=0),
    dcc.Store(id="store-total-time", data=0),
], style=CONTENT_STYLE,
id="content")


layout = html.Div([
    html.H1("Addition", style=HEADER_STYLE),
    content
])

def make_answers(level):
    if level == levels[0]:
        first = random.randint(0, 10)
        second = random.randint(0, 10 - first)
    elif level == levels[1]:
        first = random.randint(0, 10)
        second = random.randint(0, 10)
    elif level == levels[2]:
        first = random.randint(0, 99)
        second = random.randint(0, 99)
    else:
        raise ValueError("Unknown level: " + str(level))
    answer = first + second
    answer_options = [answer] + [random.randint(0, 15) for n in range(3)]
    random.shuffle(answer_options)
    return [first, second], answer, answer_options

@callback(
    Output("content", "children"),
    Output("store-answer", "data"),
    Input("button-start", "n_clicks"),
    State("level", "value"),
    prevent_initial_call=True
)
def start_quiz(n_clicks, level):
    # make questions
    question, answer, answer_options = make_answers(level)

    # display questions
    content_children = html.Div([
        html.H1(f"{question[0]} + {question[1]} = ?", className="text-center"),
        html.Br(), html.Br(),  # adds line breaks
        dbc.Row([
            dbc.Col(dbc.Button(answer_options[0], size="lg", className="w-100"), className="w-50"),
            dbc.Col(dbc.Button(answer_options[1], size="lg", className="w-100"), className="w-50"),
        ]),
        html.Br(), html.Br(),  # adds line breaks
        dbc.Row([
            dbc.Col(dbc.Button(answer_options[2], size="lg", className="w-100"), className="w-50"),
            dbc.Col(dbc.Button(answer_options[3], size="lg", className="w-100"), className="w-50"),
        ]),
    ])
    return content_children, answer

