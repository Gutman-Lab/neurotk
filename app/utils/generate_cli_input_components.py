from dash import html, dcc
import dash_bootstrap_components as dbc
import xml.etree.ElementTree as ET


def generate_cli_input_components(
    xml_string: str,
    params: dict | None = None,
    # paramSetsToIgnore=("Frame and Style", "Dask", "Girder API URL and Key"),
    # disabled=False,
    # params=None,
) -> tuple[list, bool]:
    """Generate the CLI input components from the xml string.

    Args:
        xml_string (str): The xml string to parse.
        params (dict, optional): The parameters to set the default values for. Defaults to None.

    Returns:
        list: The list of dash components to render.

    """
    # If parameters are passed then the inputs should be disabled.
    disabled = False if params is None else True

    params = {} if params is None else params

    # Format the xml string.
    root = ET.fromstring(xml_string)

    components = [
        html.H4("Inputs", className="card-title", style={"textAlign": "center"}),
    ]

    region_flag = False

    for param in root.findall(".//parameters"):
        if param.find("label") is not None and param.find("label").text != "IO":
            continue

        for parameter in param:
            label_component = None
            input_component = None
            tooltip_text = (
                parameter.find("description").text
                if parameter.find("description") is not None
                else None
            )

            tag = parameter.tag

            if tag in ("integer", "float"):
                # Integer / float style input.
                label = parameter.find("label").text

                input_id = parameter.find("name").text

                value = (
                    params[input_id]
                    if input_id in params
                    else parameter.find("default").text
                )

                if tag == "integer":
                    label += " (integer)"
                    value = int(value)
                    step = 1
                else:
                    label += " (number)"
                    value = float(value)
                    step = 0.1

                label_component = html.Label(label)
                input_component = dcc.Input(
                    type="number",
                    step=step,
                    id={"type": "dynamic-input", "index": input_id},
                    value=value,
                    disabled=disabled,
                )
            elif tag == "string":
                input_id = parameter.find("name").text

                value = (
                    params[input_id]
                    if input_id in params
                    else parameter.find("default").text
                )

                label_component = html.Label(parameter.find("label").text + " (text)")
                input_component = dcc.Input(
                    type="text",
                    id={"type": "dynamic-input", "index": input_id},
                    value=value,
                    disabled=disabled,
                )
            elif tag == "string-enumeration":
                # These are specific options you can choose.
                input_id = parameter.find("name").text

                value = (
                    params[input_id]
                    if input_id in params
                    else parameter.find("default").text
                )

                label_component = html.Label(parameter.find("label").text)

                options = [elem.text for elem in parameter.findall("element")]

                input_component = dcc.Dropdown(
                    id={"type": "dynamic-input", "index": input_id},
                    options=[{"label": op, "value": op} for op in options],
                    value=value,
                    clearable=False,
                    style={"minWidth": 300},
                    disabled=disabled,
                )
            elif tag == "region":
                region_flag = True

            if label_component is not None and input_component is not None:
                components.append(
                    html.Div(
                        dbc.Row(
                            [
                                dbc.Col(label_component, width="auto"),
                                dbc.Col(input_component, width="auto"),
                            ],
                            justify="start",
                            align="center",
                        ),
                        style={"marginTop": 10},
                    )
                )

                if tooltip_text is not None:
                    tooltip = dbc.Tooltip(
                        tooltip_text,
                        target={"type": "dynamic-input", "index": input_id},
                    )

                    components.append(tooltip)

    return components, region_flag
