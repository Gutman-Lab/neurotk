from dash import html
import dash_bootstrap_components as dbc
import callbacks.modals.delete_task_modal_callbacks

delete_task_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    "Delete task?", style={"fontWeight": "bold"}
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete",
                                    color="danger",
                                    id="delete-task-modal-btn",
                                ),
                                width="auto",
                            ),
                        ],
                        justify="start",
                        align="center",
                    )
                ),
            ],
            id="delete-task-modal",
            is_open=False,
        )
    ]
)
