from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid

images_table = AgGrid(
    id="images-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=True,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "multiple",
    },
    style={"height": "50vh"},
)

images_table_tab = html.Div(
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
