import cv2
import os
import supervisely as sly
from typing import Any, Dict
import supervisely.app.development as sly_app_development
from supervisely.app.widgets import Container, Switch, Field, Slider, Text
import numpy as np
from dotenv import load_dotenv


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
    load_dotenv(os.path.expanduser("~/supervisely_umar.env"))
    sly_app_development.supervisely_vpn_network(action="up")
    sly_app_development.create_debug_task(team_id, port="8000")

# Creating cache for project meta and images as numpy arrays.
project_metas = {}
images_cache = {}


@app.event(sly.Event.Brush.DrawLeftMouseReleased)
def brush_left_mouse_released(api: sly.Api, event: sly.Event.Brush.DrawLeftMouseReleased):
    sly.logger.info("Left mouse button released after drawing mask with brush")
    if not need_processing.is_on():
        # Checking if the processing is turned on in the UI.
        return

    if event.is_erase:
        # If the eraser was used, then we don't need to process the label in this tutorial.
        return

    processing_text.show()

    # Get project meta (using simple cache) to create sly.Label object.
    project_meta = get_project_meta(api, event.project_id)

    # Get image numpy array (using simple cache) to process the label.
    image_np = get_image_np(api, event.image_id)

    # Get sly.Label object with actual mask from Supervisely API.
    label = get_label(project_meta, event.geometry_type, event.geometry, event.object_class_title)

    # Processing the label.
    # You need to implement your own logic in the process_label function.
    new_label = process(label, image_np)

    # Upload the label with the updated mask to Supervisely platform.
    api.annotation.update_label(event.label_id, new_label)

    processing_text.hide()


def get_label(
    project_meta: sly.ProjectMeta, geometry_type: str, geometry: Dict[str, Any], class_title: str
) -> sly.Label:
    data = {
        "geometryType": geometry_type,
        "classTitle": class_title,
        "tags": [],
    }

    data.update(geometry)

    print(data)

    return sly.Label.from_json(data, project_meta)


def process(label: sly.Label, image_np: np.ndarray) -> sly.Label:
    """Processing sly.Label object and returning the processed one.

    :param label: sly.Label object to process.
    :type label: sly.Label
    :param image_np: Image numpy array.
    :type image_np: np.ndarray
    :return: Processed sly.Label object.
    :rtype: sly.Label
    """
    # In this tutorial we'll be working with masks, but you can implement your own
    # logic to edit the label (e.g. work with geometry, tags).

    # Retrieving image size from numpy array to create a full image size mask.
    image_size = image_np.shape[:2]

    # Object mask is stored in optimized form, let's unpack it.
    mask = label.get_mask(image_size)

    # Reading the strength of the dilation operation from the UI
    # and applying it to the mask.
    dilation = cv2.dilate(mask.astype(np.uint8), None, iterations=dilation_strength.get_value())

    # Returning a new label with the processed data.
    return label.clone(geometry=sly.Bitmap(data=dilation.astype(bool)))


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


def get_image_np(api: sly.Api, image_id: int) -> np.ndarray:
    """Retrieving image numpy array: if cached, then return from cache, else retrieve from Supervisely API.

    :param api: Supervisely API object.
    :type api: sly.Api
    :param image_id: Image ID for which to retrieve numpy array.
    :type image_id: int
    :return: Image numpy array.
    :rtype: np.ndarray
    """
    if len(images_cache) > 100:
        # Clearing the cache if it's too big.
        images_cache.clear()
    if image_id not in images_cache:
        image_np = api.image.download_np(image_id)
        images_cache[image_id] = image_np
    else:
        image_np = images_cache[image_id]
    return image_np


@need_processing.value_changed
def processing_switched(is_switched):
    sly.logger.debug(f"Processing is now {is_switched}")


@dilation_strength.value_changed
def strength_changed(value):
    sly.logger.debug(f"Strength is now {value}")
