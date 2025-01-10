from dash import html
import dash_bootstrap_components as dbc
import callbacks.modals.delete_dataset_modal_callbacks

delete_dataset_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    "Delete dataset?",
                                    style={"fontWeight": "bold"},
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete",
                                    color="danger",
                                    id="delete-dataset-modal-btn",
                                ),
                                width="auto",
                            ),
                        ],
                        align="center",
                        justify="start",
                    )
                ),
            ],
            id="delete-dataset-modal",
            is_open=False,
        )
    ]
)
