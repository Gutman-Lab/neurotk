from dash import dcc, html

stores = html.Div([dcc.Store(id="user-store", storage_type="local", data={})])
