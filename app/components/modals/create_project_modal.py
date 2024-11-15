from dash import html
import dash_bootstrap_components as dbc
import callbacks.modals.create_project_modal_callbacks

create_project_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Create project"),
                dbc.ModalBody(
                    [
                        html.Div(
                            "Project name",
                            style={
                                "margin": 5,
                                "marginTop": 5,
                                "fontWeight": "bold",
                            },
                        ),
                        dbc.Input(
                            id="new-project-name",
                            type="text",
                            placeholder="Enter project name",
                            style={"margin": 5},
                        ),
                        html.Div(
                            "Project name exists.",
                            hidden=True,
                            id="create-project-failed",
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
                                    id="close-create-project-modal",
                                )
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Create",
                                    className="me-1",
                                    color="primary",
                                    id="create-project-modal-btn",
                                )
                            ),
                        ]
                    )
                ),
            ],
            is_open=False,
            id="create-project-modal",
        )
    ]
)
