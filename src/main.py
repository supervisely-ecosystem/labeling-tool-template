import supervisely as sly
from fastapi import Request

from supervisely.app.widgets import Container, Text

test_text = Text("Hello, World!")

layout = Container(widgets=[test_text])

app = sly.Application(layout=layout)

server = app.get_server()


@server.post("/manual_selected_figure_changed")
def debug(request: Request):
    print(f"Manual selected figure changed, request: {request}")
    print(f"Dir of request: {dir(request)}")

    state = request.state

    сontext = request.state.context
    print(f"Context: {сontext}")

    print(f"State: {state}")

    print(f"Dir of state: {dir(state)}")

    values = request.values

    print(f"Values: {values}")

    api = state.api
    print(f"API: {api}")

    app_state = state.state

    print(f"App state: {app_state}")

    # request.json()


# @server.post("/brush_tool_released")
# def brush_tool_released(request: Request):
#     print(f"Brush tool released, request: {request}")


# @server.post("/eraser_tool_released")
# def eraser_tool_released(request: Request):
#     print(f"Eraser tool released, request: {request}")
