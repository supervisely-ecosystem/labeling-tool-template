import supervisely as sly
from fastapi import Request

from supervisely.app.widgets import Container, Text

test_text = Text("Hello, World!")

layout = Container(widgets=[test_text])

app = sly.Application(layout=layout)

server = app.get_server()


@server.post("/manual_selected_figure_changed")
async def debug(request: Request):
    print(f"Manual selected figure changed, request: {request}")
    print(f"Dir of request: {dir(request)}")

    state = request.state

    print(f"State: {state}")

    print(f"Dir of state: {dir(state)}")

    api = state.api
    print(f"API: {api}")
    state = state.state


# @server.post("/brush_tool_released")
# def brush_tool_released(request: Request):
#     print(f"Brush tool released, request: {request}")


# @server.post("/eraser_tool_released")
# def eraser_tool_released(request: Request):
#     print(f"Eraser tool released, request: {request}")
