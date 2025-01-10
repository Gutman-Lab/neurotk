from dash import html
import dash_bootstrap_components as dbc
import callbacks.modals.delete_project_modal_callbacks

delete_project_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    "Delete project?",
                                    style={"fontWeight": "bold"},
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete",
                                    color="danger",
                                    id="delete-project-modal-btn",
                                ),
                                width="auto",
                            ),
                        ],
                        justify="start",
                        align="center",
                    )
                ),
            ],
            id="delete-project-modal",
            is_open=False,
        )
    ]
)
