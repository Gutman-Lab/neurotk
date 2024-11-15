from dash_ag_grid import AgGrid

project_table = AgGrid(
    id="project-images-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=False,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
    },
    style={"height": "50vh"},
)
