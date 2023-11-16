import cv2
import os
import supervisely as sly
import supervisely.app.development as sly_app_development
from supervisely.app.widgets import Container, Switch, Field, Slider
from fastapi import Request
from typing import Any, Dict, Literal
import numpy as np
from dotenv import load_dotenv


# Creating widget to turn on/off the processing of labels.
need_processing = Switch(switched=True)

# Creating widget to set the strength of the processing.
strength = Slider(value=3, min=1, max=20, step=1)
field = Field(
    title="Process labels",
    description="If turned on, then label will be processed after creating it with bitmap brush tool",
    content=Container(widgets=[need_processing, strength]),
)

layout = Container(widgets=[field])
app = sly.Application(layout=layout)
server = app.get_server()

# Enabling advanced debug mode.
# Learn more: https://developer.supervisely.com/app-development/advanced/advanced-debugging
team_id = 448
load_dotenv(os.path.expanduser("~/supervisely.env"))
sly_app_development.supervisely_vpn_network(action="up")
sly_app_development.create_debug_task(team_id, port="8000")

# Creating cache for project meta.
project_metas = {}


def get_project_meta(api: sly.Api, project_id: int) -> sly.ProjectMeta:
    """Retrieving project meta: if cached, then return from cache, else retrieve from Supervisely API.

    :param api: Supervisely API object.
    :type api: sly.Api
    :param project_id: Project ID.
    :type project_id: int
    :return: Project meta of the project with the given ID.
    :rtype: sly.ProjectMeta
    """
    if project_id not in project_metas:
        project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))
        project_metas[project_id] = project_meta
    else:
        project_meta = project_metas[project_id]
    return project_meta


@need_processing.value_changed
def processing_switched(is_switched):
    sly.logger.info(f"Processing is now {is_switched}")


@strength.value_changed
def strength_changed(value):
    sly.logger.info(f"Strength is now {value}")


@server.post("/tools_bitmap_brush_figure_changed")
def brush_figure_changed(request: Request):
    sly.logger.info("Bitmap brush figure changed")
    request_state = request.state

    # Retrieve API and context from request.
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    # Retrieve tool state and option from context.
    tool_state = context.get("toolState", {})
    tool_option = tool_state.get("option")

    # Tool option represents if the brush or the eraser was used.
    tool_option: Literal["fill", "erase"]

    if tool_option != "fill":
        # If the eraser was used, then we don't need to process the label.
        return

    if not need_processing.is_switched():
        # Checking if the processing is turned on in the UI.
        return

    # Retrieving necessary data from context to create sly.Label object.
    label_id = context.get("figureId")
    project_id = context.get("projectId")

    # Retrieving project meta to create sly.Label object.
    project_meta = get_project_meta(api, project_id)

    # Retrieving sly.Label object from Supervisely API.
    label = api.annotation.get_label_by_id(label_id, project_meta)

    # Processing the label.
    # You need to implement your own logic in the process_label function.
    label = process_label(label)

    # Updating the label in Supervisely API after processing.
    api.annotation.update_label(label_id, label)


def process_label(label: sly.Label) -> sly.Label:
    """Processing sly.Label object and returning the processed one.

    :param label: sly.Label object to process.
    :type label: sly.Label
    :return: Processed sly.Label object.
    :rtype: sly.Label
    """
    # Implement your logic here.
    dilation_strength = strength.get_value()
    dilation = cv2.dilate(
        label.geometry.data.astype(np.uint8), None, iterations=dilation_strength
    )

    # Return a new label with the processed data
    return label.clone(
        geometry=sly.Bitmap(data=dilation.astype(bool), origin=label.geometry.origin)
    )
