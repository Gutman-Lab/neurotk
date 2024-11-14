from dash import html, dcc
from components.tasks_tab_tabs.results_annotation_tab import (
    results_annotation_tab,
)

results_tab = html.Div(
    [
        dcc.Tabs(
            value="annotations",
            children=[
                dcc.Tab(
                    label="Annotations",
                    value="annotations",
                    children=results_annotation_tab,
                    style={"width": "100%"},
                ),
            ],
            vertical=True,
        )
    ]
)
