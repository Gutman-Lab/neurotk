from dash import html
import dash_bootstrap_components as dbc
import callbacks.modals.create_task_modal_callbacks

create_task_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Create task"),
                dbc.ModalBody(
                    [
                        html.Div(
                            "Task name",
                            style={
                                "margin": 5,
                                "marginTop": 5,
                                "fontWeight": "bold",
                            },
                        ),
                        dbc.Input(
                            id="new-task-name",
                            type="text",
                            placeholder="Enter task name",
                            style={"margin": 5},
                        ),
                        html.Div(
                            "Task name exists.",
                            hidden=True,
                            id="create-task-failed",
                            style={
                                "color": "red",
                                "fontWeight": "bold",
                                "margin": 10,
                            },
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
                                    id="close-create-task-modal",
                                )
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Create",
                                    className="me-1",
                                    color="primary",
                                    id="create-task-modal-btn",
                                )
                            ),
                        ]
                    )
                ),
            ],
            id="create-task-modal",
        )
    ]
)
