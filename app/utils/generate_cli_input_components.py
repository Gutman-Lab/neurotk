from dash import html, dcc
import dash_bootstrap_components as dbc
import xml.etree.ElementTree as ET


def generate_cli_input_components(
    xml_string: str,
    params: dict | None = None,
) -> tuple[list, bool]:
    """Generate the CLI input components from the xml string.

    Args:
        xml_string (str): The xml string to parse.
        params (dict, optional): The parameters to set the default values for. Defaults to None.

    Returns:
        list: The list of dash components to render.

    """
    # If parameters are passed then disable the inputs fields.
    disabled = not params is None

    # Format the xml string.
    root = ET.fromstring(xml_string)

    rows = []
    # tooltips = []  # tool tip causing errors when switching between CLIs

    for param in root.findall(".//parameters"):
        if (
            param.find("label") is not None
            and param.find("label").text != "I/O"
        ):
            continue

        for parameter in param:
            label_component = None
            input_component = None

            tag = parameter.tag

            if tag in ("integer", "float"):
                # Integer / float style input.
                label = parameter.find("label").text

                input_id = parameter.find("name").text

                if params is None:
                    value = parameter.find("default").text
                else:
                    value = params[input_id]

                if tag == "integer":
                    label += " (integer):"
                    value = int(value)
                    step = 1
                else:
                    label += " (number):"
                    value = float(value)
                    step = 0.01

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

                if params is None:
                    value = parameter.find("default").text
                else:
                    value = params[input_id]

                label_component = html.Label(
                    parameter.find("label").text + " (text):"
                )
                input_component = dcc.Input(
                    type="text",
                    id={"type": "dynamic-input", "index": input_id},
                    value=value,
                    disabled=disabled,
                )
            elif tag == "string-enumeration":
                # These are specific options you can choose.
                input_id = parameter.find("name").text

                if params is None:
                    value = parameter.find("default").text
                else:
                    value = params[input_id]

                label_component = html.Label(parameter.find("label").text + ":")

                options = [elem.text for elem in parameter.findall("element")]

                input_component = dcc.Dropdown(
                    id={"type": "dynamic-input", "index": input_id},
                    options=[{"label": op, "value": op} for op in options],
                    value=value,
                    clearable=False,
                    style={"minWidth": 250},
                    disabled=disabled,
                )

            if label_component is not None and input_component is not None:
                rows.append(
                    dbc.Row(
                        [
                            dbc.Col(label_component, width=6),
                            dbc.Col(input_component, width=6),
                        ],
                        justify="start",
                        align="center",
                        style={"marginBottom": 10},
                    )
                )

                # Check if there is a description for the parameter.
                # description = parameter.find("description")

                # if description is not None:
                #     description_text = description.text

                # tooltips.append(
                #     dbc.Tooltip(
                #         description_text,
                #         target={"type": "dynamic-input", "index": input_id},
                #     )
                # )

    # Extend the rows with the tooltips.
    # rows.extend(tooltips)

    return html.Div(rows)
