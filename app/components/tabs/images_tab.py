from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
from components.images_table import images_table

import callbacks.update_task_dropdown
import callbacks.load_cli_inputs

images_tab = html.Div(
    [
        dbc.Row(
            dcc.RadioItems(
                ["All Project Images", "Task Images", "Images not in Task"],
                inline=True,
                inputStyle={"marginLeft": 15, "marginRight": 5},
                value="All Project Images",
                id="images-radio",
            )
        ),
        images_table,
    ],
)
