import supervisely as sly

from supervisely.app.widgets import Container, Text

test_text = Text("Hello, World!")

layout = Container(widgets=[test_text])

app = sly.Application(layout=layout)
