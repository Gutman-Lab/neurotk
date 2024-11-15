from dash import html, dcc
import dash_bootstrap_components as dbc
import callbacks.modals.add_dataset_modal_callbacks

add_dataset_modal = dbc.Modal(
    [
        dbc.ModalHeader("Add Dataset"),
        dbc.ModalBody(
            [
                html.Div(
                    "Dataset",
                    style={"margin": 5, "marginTop": 5, "fontWeight": "bold"},
                ),
                dcc.Dropdown(
                    id="add-dataset-dropdown", options=[], clearable=False
                ),
            ]
        ),
        dbc.ModalFooter(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Close",
                            className="me-1",
                            color="light",
                            id="close-add-dataset-modal",
                        )
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Add",
                            className="me-1",
                            color="primary",
                            id="add-dataset-modal-btn",
                        )
                    ),
                ]
            )
        ),
    ],
    id="add-dataset-modal",
    is_open=False,
)
