import supervisely as sly
from fastapi import Request
from typing import Any, Dict, Literal

from supervisely.app.widgets import Container, Switch, Field

# Creating widget to turn on/off the processing of labels.
process_labels = Switch(switched=True)
process_labels_field = Field(
    title="Process labels",
    description="If turned on, then label will be processed after creating it with bitmap brush tool",
    content=process_labels,
)

layout = Container(widgets=[process_labels_field])

app = sly.Application(layout=layout)

server = app.get_server()


@process_labels.value_changed
def debug(is_switched):
    sly.logger.info(f"Processing is now {is_switched}")


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

    if not process_labels.is_switched():
        # Checking if the processing is turned on in the UI.
        return

    # Retrieving necessary data from context to create sly.Label object.
    class_title = context.get("figureClassTitle")
    label_id = context.get("figureId")
    project_id = context.get("projectId")

    # Retrieving project meta to create sly.Label object.
    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    # Retrieving sly.Label object from Supervisely API.
    label = api.annotation.get_image_label_by_id(label_id, class_title, project_meta)

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
    return label.translate(10, 10)
