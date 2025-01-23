import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
from dash import html, dcc
from dash_paperdragon import DashPaperdragon
from config import DASH_PAPERDRAGON_CONFIG

import callbacks.update_task_tab_tables
import callbacks.deselect_table_row
import callbacks.update_annotation_tab_image_viewer

annotation_tab_tables_and_img_viewer = dbc.Row(
    [
        dcc.Store(id="trigger-by-sync-ann", data=True),
        dbc.Col(
            [
                html.Div(
                    "With Document",
                    style={"textAlign": "center", "fontWeight": "bold"},
                ),
                AgGrid(
                    id="imgs-with-ann-table",
                    columnDefs=[
                        {"headerName": "Name", "field": "name"},
                        {"headerName": "ID", "field": "_id"},
                    ],
                    rowData=[],
                    enableEnterpriseModules=True,
                    dashGridOptions={
                        "pagination": True,
                        "paginationAutoPageSize": True,
                        "enableCellTextSelection": True,
                        "ensureDomOrder": True,
                        "rowSelection": "single",
                    },
                    style={"height": "50vh"},
                ),
            ],
            width=3,
        ),
        dbc.Col(
            [
                html.Div(
                    "Without Document",
                    style={"textAlign": "center", "fontWeight": "bold"},
                ),
                AgGrid(
                    id="imgs-without-ann-table",
                    columnDefs=[
                        {"headerName": "Name", "field": "name"},
                        {"headerName": "ID", "field": "_id"},
                    ],
                    rowData=[],
                    enableEnterpriseModules=True,
                    dashGridOptions={
                        "pagination": True,
                        "paginationAutoPageSize": True,
                        "enableCellTextSelection": True,
                        "ensureDomOrder": True,
                        "rowSelection": "single",
                    },
                    style={"height": "50vh"},
                ),
            ],
            width=3,
        ),
        dbc.Col(
            [
                dbc.Button(
                    "Show annotations",
                    id="show-ann-btn",
                    style={"marginBottom": 10},
                ),
                DashPaperdragon(
                    id="ann-tab-img-viewer",
                    zoomLevel=0,
                    config=DASH_PAPERDRAGON_CONFIG,
                    viewportBounds={"x": 0, "y": 0, "width": 0, "height": 0},
                    outputFromPaper={},
                    curMousePosition={"x": 0, "y": 0},
                    viewerWidth=600,
                ),
            ],
            width=6,
        ),
    ],
    style={"marginTop": 10},
)
