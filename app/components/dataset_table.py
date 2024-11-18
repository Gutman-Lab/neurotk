from dash_ag_grid import AgGrid

dataset_table = AgGrid(
    id="dataset-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=True,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "enableCellTextSelection": True,
        "ensureDomOrder": True,
    },
    style={"height": "50vh"},
)
