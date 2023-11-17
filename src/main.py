import cv2
import os
import supervisely as sly
import supervisely.app.development as sly_app_development
from supervisely.app.widgets import Container, Switch, Field, Slider
from typing import Literal, Tuple
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
strength = Slider(value=10, min=1, max=50, step=1)
strength_field = Field(
    title="Dilation",
    description="Select the strength of the dilation operation",
    content=strength,
)

layout = Container(widgets=[processing_field, strength_field])
app = sly.Application(layout=layout)

# Enabling advanced debug mode.
# ! (updated docs) Learn more: https://developer.supervisely.com/app-development/advanced/advanced-debugging
if sly.is_development():
    load_dotenv("local.env")
    team_id = sly.env.team_id()
    load_dotenv(os.path.expanduser("~/supervisely.env"))
    sly_app_development.supervisely_vpn_network(action="up")
    sly_app_development.create_debug_task(team_id, port="8000")

# Creating cache for project meta.
project_metas = {}
image_nps = {}


@app.event(sly.Events.BRUSH_DRAW_LEFT_MOUSE_RELEASE)
def brush_figure_changed(api: sly.Api, context: sly.Context):
    sly.logger.info("Bitmap brush figure changed")
    if not need_processing.is_on():
        # Checking if the processing is turned on in the UI.
        return

    # Retrieve option from context.
    # Tool option represents if the brush or the eraser was used.
    tool_option = context.tool_option
    tool_option: Literal["fill", "erase"]

    if tool_option != "fill":
        # If the eraser was used, then we don't need to process the label.
        return

    # Retrieving necessary data from context to create sly.Label object.
    object_id = context.object_id
    project_id = context.project_id
    image_id = context.image_id

    # Retrieving project meta to create sly.Label object.
    project_meta = get_project_meta(api, project_id)

    # Retrieving image numpy array to process the label.
    image_np = get_image_np(api, image_id)

    # Retrieving sly.Label object from Supervisely API.
    label = api.annotation.get_label_by_id(object_id, project_meta)

    # Processing the label.
    # You need to implement your own logic in the process_label function.
    new_label = process_label(label, image_np)

    # Updating the label in Supervisely API after processing.
    api.annotation.update_label(object_id, new_label)


def process_label(label: sly.Label, image_np: np.ndarray) -> sly.Label:
    """Processing sly.Label object and returning the processed one.

    :param label: sly.Label object to process.
    :type label: sly.Label
    :param image_np: Image numpy array.
    :type image_np: np.ndarray
    :return: Processed sly.Label object.
    :rtype: sly.Label
    """
    # Retrieving image size from numpy array to create a full image size mask.
    image_height, image_width = image_np.shape[:2]

    # Creating a full image size mask from the label mask.
    mask = get_full_image_mask(
        (image_height, image_width),
        label.geometry.data.astype(np.uint8),
        label.geometry.origin.row,
        label.geometry.origin.col,
    )

    # Reading the strength of the dilation operation from the UI
    # and applying it to the mask.
    dilation_strength = strength.get_value()
    dilation = cv2.dilate(mask, None, iterations=dilation_strength)

    # Returning a new label with the processed data
    return label.clone(geometry=sly.Bitmap(data=dilation.astype(bool)))


def get_full_image_mask(
    image_size: Tuple[int, int], mask: np.ndarray, row: int, col: int
) -> np.ndarray:
    """Creating a full image size mask from the mask with origin.

    :param image_size: Image size in pixels (height, width)
    :type image_size: Tuple[int, int]
    :param mask_with_origin: Mask with origin.
    :type mask_with_origin: np.ndarray
    :param row: Origin row.
    :type row: int
    :param col: Origin column.
    :type col: int
    :return: Full image size mask.
    :rtype: np.ndarray
    """
    new_mask = np.zeros((image_size), dtype=np.uint8)
    new_mask[
        row : row + mask.shape[0],
        col : col + mask.shape[1],
    ] = mask
    return new_mask


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
    if image_id not in image_nps:
        image_np = api.image.download_np(image_id)
        image_nps[image_id] = image_np
    else:
        image_np = image_nps[image_id]
    return image_np


@need_processing.value_changed
def processing_switched(is_switched):
    sly.logger.info(f"Processing is now {is_switched}")


@strength.value_changed
def strength_changed(value):
    sly.logger.info(f"Strength is now {value}")
