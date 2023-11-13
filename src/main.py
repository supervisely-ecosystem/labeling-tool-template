import supervisely as sly

from supervisely.app.widgets import Container

import src.ui.input as input

layout = Container(widgets=[input.card])

app = sly.Application(layout=layout)
