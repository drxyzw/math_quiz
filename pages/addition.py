import dash
from dash import html, dcc, callback, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import random
from datetime import datetime as dt

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
    dbc.Button("Start", id={"type": "button-start", "index": 0}, size="lg", n_clicks=0, className="w-100"),
    html.Br(), html.Br(),  # adds line breaks
    dcc.RadioItems(id="level",
                   options=levels,
                    value=levels[0]),
], style=CONTENT_STYLE,
id="content")

status_content = html.Div([], id="status-content")

layout = html.Div([
    html.H1("Addition", style=HEADER_STYLE),
    content,
    status_content,
    dcc.Store(id="store-data", data={
        "level": levels[0],
        "total_count": 10,
        "historical_count": 0,
        "correct_count": 0,
        "incorrect_count": 0,
        "historical_questions": [[]],
        "historical_true_answers": [],
        "historical_answers": [],
        "current_timer": 0,
        "current_start_time": 0,
        "total_time": 0,
    }),
])

@callback(
        Output("store-data", "data", allow_duplicate=True),
        Input("level", "value"),
        State("store-data", "data"),
        prevent_initial_call=True,
)
def update_level(value, data):
    data["level"] = value
    return data

def generate_rand_int_array(size, min, max, required):
    initial_sample = random.sample(range(min, max + 1), size)
    if required not in initial_sample:
        initial_sample[random.randint(0, size-1)] = required
    return initial_sample

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
    true_answer = first + second
    answer_options = generate_rand_int_array(4, 0, 20, true_answer)
    return [first, second], true_answer, answer_options

@callback(
    Output("content", "children", allow_duplicate=True),
    Output("store-data", "data", allow_duplicate=True),
    Input({"type": "button-start", "index": ALL}, "n_clicks"),
    Input({"type": "button-next", "index": ALL}, "n_clicks"),
    State("store-data", "data"),
    prevent_initial_call=True
)
def start_quiz(n_clicks_start, n_clicks_next, data):
    # ignore call rom button-next, but not actually clicked
    triggered_id = ctx.triggered_id
    if (triggered_id and isinstance(triggered_id, dict)
        and triggered_id.get("type") == "button-next"):
        if n_clicks_next[0] is None:
            raise dash.exceptions.PreventUpdate
        elif data["historical_count"] == data["total_count"]:
            raise dash.exceptions.PreventUpdate

    # make questions
    level = data["level"]
    question, true_answer, answer_options = make_answers(level)

    # save to store-data
    data["current_start_time"] = dt.now()
    data['historical_count'] += 1
    data['historical_questions'].append([question[0], question[1]])
    data["historical_true_answers"].append(true_answer)

    # display questions
    content_children = html.Div([
        html.H1(f"{question[0]} + {question[1]} = ?", className="text-center"),
        html.Br(), html.Br(),  # adds line breaks
        dbc.Row([
            dbc.Col(dbc.Button(answer_options[0], id={"type": "answer-button", "index": 0}, size="lg", className="w-100"), className="w-50"),
            dbc.Col(dbc.Button(answer_options[1], id={"type": "answer-button", "index": 1}, size="lg", className="w-100"), className="w-50"),
        ]),
        html.Br(), html.Br(),  # adds line breaks
        dbc.Row([
            dbc.Col(dbc.Button(answer_options[2], id={"type": "answer-button", "index": 2}, size="lg", className="w-100"), className="w-50"),
            dbc.Col(dbc.Button(answer_options[3], id={"type": "answer-button", "index": 3}, size="lg", className="w-100"), className="w-50"),
        ]),
    ])
    return content_children, data

@callback(
    Output("content", "children"),
    Output("store-data", "data", allow_duplicate=True),
    Output("status-content", "children"),
    Input({"type": "answer-button", "index": ALL}, "n_clicks"),
    State({"type": "answer-button", "index": ALL}, "children"),
    State("store-data", "data"),
    prevent_initial_call=True,
)
def evaluate_answer(n_clicks_inputs, values, data):
    trigger_id = ctx.triggered_id
    if (trigger_id is None) or (isinstance(trigger_id, dict) and trigger_id.get("type") != "answer-button"):
        raise dash.exceptions.PreventUpdate

    # filter button with clicks
    clicked = [i for (i, k) in enumerate(n_clicks_inputs) if k]
    if not clicked:
        raise dash.exceptions.PreventUpdate
    i = clicked[0]
    answer = values[i]
    data['historical_answers'].append(answer)
    
    true_answer = data['historical_true_answers'][-1]
    question = data['historical_questions'][-1]
    isFinal = data['historical_count'] == data['total_count']
    if true_answer == answer: # correct answer
        data["correct_count"] += 1
        content = html.Div([
            html.H1([
                html.Span(f"{question[0]} + {question[1]} = "),
                html.Span(f"{answer}", style={"color": "limegreen"}),
                "✅",
                html.H1("Correct!"),
                (
                    html.Div([
                        dbc.Button("Start again", id={"type": "button-restart", "index": 0}, size="lg",  className="w-100"),
                        dcc.Location(id='url', refresh=True),
                    ])
                    if isFinal else 
                    dbc.Button("Next", id={"type": "button-next", "index": 0}, size="lg",  className="w-100")
                ),
            ], className="text-center"),
        ])
    else:
        data["incorrect_count"] += 1
        content = html.Div([
            html.H1([
                html.Span(f"{question[0]} + {question[1]} = "),
                html.Span(f"{answer}", style={"color": "red"}),
                "❌",
                html.H1("Incorrect!"),
                (
                    html.Div([
                        dbc.Button("Start again", id={"type": "button-restart", "index": 0}, size="lg",  className="w-100"),
                        dcc.Location(id='url', refresh=True),
                    ])
                    if isFinal else 
                    dbc.Button("Next", id={"type": "button-next", "index": 0}, size="lg",  className="w-100")
                ),
            ], className="text-center"),
        ])
    
    finished = data["historical_count"]
    correct = data["correct_count"]
    incorrect = data["incorrect_count"]
    status = html.Div([
        html.H1(f"Finished: {finished}, correct: {correct}, incorrect: {incorrect}")
    ])

    return content, data, status

@callback(
    Output("url", "href"),
    Input({"type": "button-restart", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def reload_page(n_clicks_inputs):
    return "/addition"
