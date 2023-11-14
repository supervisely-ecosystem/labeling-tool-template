import supervisely as sly
from fastapi import Request
from typing import Any, Dict

from supervisely.app.widgets import Container, Editor

from src.saver import get_figure_by_id, update_figure

logger_widget = Editor(
    "Logs:", height_px=200, language_mode="plain_text", readonly=True
)

layout = Container(widgets=[logger_widget])

app = sly.Application(layout=layout)

server = app.get_server()


def set_log_in_widget(log: str):
    text = logger_widget.get_text()
    new_text = text + "\n" + log
    logger_widget.set_text(new_text)


@server.post("/tools_bitmap_brush_figure_changed")
def brush_figure_changed(request: Request):
    request_state = request.state
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    sly.logger.info(f"Brush changed figure, context: {context}")
    set_log_in_widget(f"Brush changed figure, context: {context}")

    tool_state = context.get("toolState", {})
    tool_option = tool_state.get("option", None)

    print(f"Tool state: {tool_state}")

    if tool_option != "fill":
        return

    class_title = context.get("figureClassTitle")
    project_id = context.get("projectId")
    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    set_log_in_widget(f"Class title: {class_title}, project id: {project_id}")

    figure_id = context.get("figureId")
    sly_label = get_figure_by_id(figure_id, class_title, project_meta)

    set_log_in_widget("Retrieved sly.Label")

    sly_label = process_label(sly_label)

    set_log_in_widget("Processed sly.Label")

    update_figure(figure_id, sly_label)

    set_log_in_widget("Updated figure")


@server.post("/manual_selected_figure_changed")
def figure_changed(request: Request):
    request_state = request.state
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    sly.logger.info(f"Figure changed, context: {context}")
    set_log_in_widget(f"Figure changed, context: {context}")

    figure_id = context.get("figureId")
    class_title = context.get("figureClassTitle")
    project_id = context.get("projectId")

    sly.logger.info(
        f"Figure id: {figure_id}, class title: {class_title}, project id: {project_id}"
    )
    set_log_in_widget(
        f"Figure id: {figure_id}, class title: {class_title}, project id: {project_id}"
    )

    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    sly_label = get_figure_by_id(figure_id, class_title, project_meta)

    sly.logger.info(
        f"Type of label: {type(sly_label)} with geometry: {sly_label.geometry.name()}"
    )
    set_log_in_widget(
        f"Type of label: {type(sly_label)} with geometry: {sly_label.geometry.name()}"
    )


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
