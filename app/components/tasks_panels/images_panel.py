from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid

images_table = AgGrid(
    id="images-table",
    columnDefs=[
        {"headerName": "Image Name", "field": "name"},
        {"headerName": "Image Path", "field": "path"},
        {"headerName": "Image URL", "field": "url"},
    ],
    rowSelection="single",
    paginationPageSize=10,
    paginationAutoPageSize=True,
    domLayout="autoHeight",
    style_cell={"textAlign": "left"},
    style_header={"fontWeight": "bold"},
    style_table={"height": 300},
)

images_panel = html.Div(
    [
        dbc.Row(
            dcc.RadioItems(
                ["All Experiment Images", "Task Images"],
                inline=True,
                inputStyle={"marginLeft": 15, "marginRight": 5},
            )
        )
    ],
    style={"margin": 10},
)
