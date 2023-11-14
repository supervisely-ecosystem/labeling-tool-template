import supervisely as sly
from fastapi import Request
from typing import Any, Dict

from supervisely.app.widgets import Container, Text

from src.saver import get_figure_by_id

test_text = Text("Hello, World!")

layout = Container(widgets=[test_text])

app = sly.Application(layout=layout)

server = app.get_server()


@server.post("/tools_bitmap_brush_figure_changed")
def brush_figure_changed(request: Request):
    request_state = request.state
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    sly.logger.info(f"Brush changed figure, context: {context}")

    tool_state = context.get("toolState", {})
    tool_option = tool_state.get("option", None)

    print(f"Tool state: {tool_state}")

    if tool_state != "fill":
        return

    figure_id = context.get("figureId")
    figure = get_figure_by_id(figure_id)


@server.post("/manual_selected_figure_changed")
def figure_changed(request: Request):
    request_state = request.state
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    sly.logger.info(f"Figure changed, context: {context}")

    figure_id = context.get("figureId")
    class_title = context.get("figureClassTitle")
    project_id = context.get("projectId")

    sly.logger.info(
        f"Figure id: {figure_id}, class title: {class_title}, project id: {project_id}"
    )

    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    sly_label = get_figure_by_id(figure_id, class_title, project_meta)

    sly.logger.info(
        f"Type of label: {type(sly_label)} with geometry: {sly_label.geometry.name()}"
    )


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
