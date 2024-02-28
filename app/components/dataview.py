"""The component containing the toggle between dataview and datatable."""
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html

dataview = html.Div([
    dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.Tab("Table", value="images-tab", style={"color": "white"}),
                        dmc.Tab("Images", value="images-tab", style={"color": "white"}),
                    ],
                ),
                dmc.TabsPanel(
                    html.Div(
                        "Images tab content.",
                    ),
                    value="projects",
                ),
            ],
            orientation="horizontal",
            value="images-tab",
            color=getenv("LIGHT_BLUE"),
            # inverted=True,
            # variant="pills",
        ),
], style={'display': 'flex'})

dmc.Switch(
    size="lg",
    radius="sm",
    label="Enable this option",
    checked=True
)