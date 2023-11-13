import supervisely as sly
from fastapi import Request

from supervisely.app.widgets import Container, Text

test_text = Text("Hello, World!")

layout = Container(widgets=[test_text])

app = sly.Application(layout=layout)

server = app.get_server()


@server.post("/")
def debug(request: Request):
    print(f"Request: {request}")

    return {"status": "ok"}


# @server.post("/brush_tool_released")
# def brush_tool_released(request: Request):
#     print(f"Brush tool released, request: {request}")

#     return {"status": "ok"}


# @server.post("/eraser_tool_released")
# def eraser_tool_released(request: Request):
#     print(f"Eraser tool released, request: {request}")

#     return {"status": "ok"}
