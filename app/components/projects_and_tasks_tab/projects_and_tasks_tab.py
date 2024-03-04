from dash import html

from components.projects_and_tasks_tab.project_selection import project_selection
from components.projects_and_tasks_tab.task_selection import task_selection
from components.projects_and_tasks_tab.dataview import dataview

projects_and_tasks_tab = html.Div([project_selection, task_selection, dataview])
