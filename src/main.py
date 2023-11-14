import supervisely as sly
from fastapi import Request
from typing import Any, Dict

from supervisely.app.widgets import Container, Switch, Field, Checkbox

from src.saver import get_figure_by_id, update_figure

apply_processing = Switch()
apply_processing_field = Field(
    title="Apply processing",
    description="If turned on, then label will be processed after crating it with bitmap brush tool",
    content=apply_processing,
)

layout = Container(widgets=[apply_processing_field])

app = sly.Application(layout=layout)

server = app.get_server()


@apply_processing.value_changed
def debug(is_switched):
    sly.logger.info(f"Value changed! Is switched now: {is_switched}")
    json_state = apply_processing.get_json_state()
    sly.logger.info(f"Json state: {json_state}")


@server.post("/tools_bitmap_brush_figure_changed")
def brush_figure_changed(request: Request):
    sly.logger.info("Bitmap brush figure changed")
    request_state = request.state
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    tool_state = context.get("toolState", {})
    tool_option = tool_state.get("option")

    sly.logger.info(f"Tool state: {tool_state}, tool option: {tool_option}")

    if tool_option != "fill":
        sly.logger.info("Option is not fill, skipping")
        return

    json_state = apply_processing.get_json_state()
    sly.logger.info(f"Json state: {json_state}")

    processing_enabled = apply_processing.is_switched()
    sly.logger.info(f"Processing enabled: {processing_enabled}")
    sly.logger.info(f"Processing enabled type: {type(processing_enabled)}")

    if not processing_enabled:
        sly.logger.info("Processing is not enabled, skipping")
        return

    class_title = context.get("figureClassTitle")
    project_id = context.get("projectId")

    sly.logger.info(f"Class title: {class_title}, project id: {project_id}")

    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    figure_id = context.get("figureId")
    sly_label = get_figure_by_id(figure_id, class_title, project_meta)

    sly.logger.info(f"Retrieved sly.Label by id: {figure_id}")

    sly_label = process_label(sly_label)

    sly.logger.info(f"Processed sly.Label with id: {figure_id}")

    update_figure(figure_id, sly_label)

    sly.logger.info(f"Updated figure with id: {figure_id}")


# @server.post("/manual_selected_figure_changed")
# def figure_changed(request: Request):
#     request_state = request.state
#     api: sly.Api = request_state.api
#     context: Dict[str, Any] = request_state.context

#     sly.logger.info(f"Figure changed, context: {context}")
#     set_log_in_widget(f"Figure changed, context: {context}")

#     figure_id = context.get("figureId")
#     class_title = context.get("figureClassTitle")
#     project_id = context.get("projectId")

#     sly.logger.info(
#         f"Figure id: {figure_id}, class title: {class_title}, project id: {project_id}"
#     )
#     set_log_in_widget(
#         f"Figure id: {figure_id}, class title: {class_title}, project id: {project_id}"
#     )

#     project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

#     sly_label = get_figure_by_id(figure_id, class_title, project_meta)

#     sly.logger.info(
#         f"Type of label: {type(sly_label)} with geometry: {sly_label.geometry.name()}"
#     )
#     set_log_in_widget(
#         f"Type of label: {type(sly_label)} with geometry: {sly_label.geometry.name()}"
#     )

#     sly_label = process_label(sly_label)

#     set_log_in_widget("Processed sly.Label")

#     update_figure(figure_id, sly_label)

#     set_log_in_widget("Updated figure")


def process_label(label: sly.Label) -> sly.Label:
    # Implement your logic here.
    return label.translate(10, 10)


# {
#     "datasetId": 986,
#     "teamId": 96,
#     "workspaceId": 148,
#     "projectId": 569,
#     "imageId": 33976,
#     "figureId": 614761,
#     "figureClassId": 29347,
#     "figureClassTitle": "kiwi",
#     "toolClassId": 29347,
#     "sessionId": "8004db32-b12f-4a5b-a4d1-99f57a8b4463",
#     "tool": "bitmapBrush",
#     "userId": 89,
#     "jobId": None,
#     "toolState": {"option": "fill"},
# }
