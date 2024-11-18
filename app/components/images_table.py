from dash_ag_grid import AgGrid
import callbacks.update_images_table

images_table = AgGrid(
    id="images-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=True,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "multiple",
        "enableCellTextSelection": True,
        "ensureDomOrder": True,
    },
    style={"height": "50vh"},
)
