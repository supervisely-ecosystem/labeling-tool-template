import cv2
import os
import supervisely as sly
import supervisely.app.development as sly_app_development
from supervisely.app.widgets import Container, Switch, Field, Slider, Text
import numpy as np
from dotenv import load_dotenv
from datetime import datetime


# Creating widget to turn on/off the processing of labels.
need_processing = Switch(switched=True)
processing_field = Field(
    title="Process masks",
    description="If turned on, then the mask will be processed after every change on left mouse release after drawing",
    content=need_processing,
)

# Creating widget to set the strength of the processing.
dilation_strength = Slider(value=10, min=1, max=50, step=1)
dilation_strength_field = Field(
    title="Dilation",
    description="Select the strength of the dilation operation",
    content=dilation_strength,
)

processing_text = Text("Processing mask...", status="info")
processing_text.hide()

layout = Container(widgets=[processing_text, processing_field, dilation_strength_field])
app = sly.Application(layout=layout)

# Enabling advanced debug mode.
if sly.is_development():
    load_dotenv("local.env")
    team_id = sly.env.team_id()
    load_dotenv(os.path.expanduser("~/supervisely.env"))
    sly_app_development.supervisely_vpn_network(action="up")
    sly_app_development.create_debug_task(team_id, port="8000")

# Creating cache for project meta to avoid unnecessary requests to Supervisely API.
project_metas = {}

timestamp = None


@app.event(sly.Event.Brush.DrawLeftMouseReleased)
def brush_left_mouse_released(api: sly.Api, event: sly.Event.Brush.DrawLeftMouseReleased):
    sly.logger.info("Left mouse button released after drawing mask with brush")
    if not need_processing.is_on():
        # Checking if the processing is turned on in the UI.
        return

    if event.is_erase:
        # If the eraser was used, then we don't need to process the label in this tutorial.
        return

    # processing_text.show()
    t = datetime.now().timestamp()
    global timestamp
    timestamp = t

    # Get project meta (using simple cache) to create sly.Label object.
    project_meta = get_project_meta(api, event.project_id)

    # Retrieving object class from project meta to create sly.Label object later.
    obj_class = project_meta.get_obj_class_by_id(event.object_class_id)

    # Processing the mask. You need to implement your own logic in the process function.
    new_mask = process(event.mask)

    # Creating a new label with the updated mask.
    label = sly.Label(geometry=sly.Bitmap(data=new_mask.astype(bool)), obj_class=obj_class)

    # Upload the label with the updated mask to Supervisely platform.
    if t == timestamp:
        print("uploading")
        api.annotation.update_label(event.label_id, label)
    else:
        print("upload was throttled")

    # processing_text.hide()


def process(mask: np.ndarray) -> np.ndarray:
    """Processing the mask.

    :param mask: Mask to process.
    :type mask: np.ndarray
    :return: Processed mask.
    :rtype: np.ndarray
    """
    # Reading the strength of the dilation operation from the UI
    # and applying it to the mask.
    dilation = cv2.dilate(mask.astype(np.uint8), None, iterations=dilation_strength.get_value())

    # Returning a new mask.
    return dilation


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
    sly.logger.debug(f"Processing is now {is_switched}")


@dilation_strength.value_changed
def strength_changed(value):
    sly.logger.debug(f"Strength is now {value}")
