PIE_CHART_COLORS = dict(
    error="rgb(255, 0, 0)",
    cancelled="rgb(209, 207, 202)",
    inactive="rgb(0, 255, 238)",
    success="rgb(14, 153, 0)",
    queued="rgb(0, 141, 255)",
    running="rgb(0, 0, 255)",
    exists="rgb(181, 215, 0)",
    Submitted="rgb(255, 217, 0)",
)

COLORS = {
    "COOL_GRAY_1": "#d9d9d6",
    "EMORY_BLUE": "#012169",
    "LIGHT_BLUE": "#007dba",
    "YELLOW": "#f2a900",
}


PIE_CHART_COLOR_MAP = {
    "Inactive": "rgb(0, 255, 238)",
    "Queued": "rgb(0, 141, 255)",
    "Running": "rgb(0, 0, 255)",
    "Success": "rgb(14, 153, 0)",
    "Error": "rgb(255, 0, 0)",
    "Canceled": "rgb(209, 207, 202)",
}

CLASSES = ["a", "b", "c", "d", "e", "f"]
OSD_COCLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

DASH_PAPERDRAGON_CONFIG = {
    "eventBindings": [
        {
            "event": "keyDown",
            "key": "c",
            "action": "cycleProp",
            "property": "class",
        },
        {
            "event": "keyDown",
            "key": "x",
            "action": "cyclePropReverse",
            "property": "class",
        },
        {"event": "keyDown", "key": "d", "action": "deleteItem"},
        {
            "event": "keyDown",
            "key": "n",
            "action": "newItem",
            "tool": "rectangle",
        },
        {
            "event": "keyDown",
            "key": "e",
            "action": "editItem",
            "tool": "rectangle",
        },
        {
            "event": "mouseEnter",
            "action": "dashCallback",
            "callback": "mouseEnter",
        },
        {
            "event": "mouseLeave",
            "action": "dashCallback",
            "callback": "mouseLeave",
        },
    ],
    "callbacks": [
        {"eventName": "item-created", "callback": "createItem"},
        {"eventName": "property-changed", "callback": "propertyChanged"},
        {"eventName": "item-deleted", "callback": "itemDeleted"},
        {"eventName": "item-edited", "callback": "itemEdited"},
    ],
    "properties": {"class": CLASSES[0]},
    "defaultStyle": {
        "fillColor": OSD_COCLORS[0],
        "strokeColor": OSD_COCLORS[0],
        "rescale": {
            "strokeWidth": 1,
        },
        "fillOpacity": 0.2,
    },
    "styles": {
        "class": {
            k: {"fillColor": c, "strokeColor": c}
            for (k, c) in zip(CLASSES, OSD_COCLORS)
        }
    },
}
