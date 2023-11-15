import src.globals as g
import supervisely as sly
from time import sleep

PROJECT_ID = 31312
FIGURE_IDS = [176193265, 176193266, 176193267, 176193268, 176193269]
CLASS_TITLES = [
    "rectangle-class",
    "polyline-class",
    "polygon-class",
    "bitmap-class",
    "point-class",
]


def process_label(label: sly.Label) -> sly.Label:
    # Implement your logic here.
    return label.translate(10, 10)


project_meta = sly.ProjectMeta.from_json(g.api.project.get_meta(PROJECT_ID))
print("Project meta received.")

for figure_id, class_title in zip(FIGURE_IDS, CLASS_TITLES):
    print(f"Getting label for figure {figure_id} with class {class_title}")
    label = g.api.annotation.get_image_label_by_id(figure_id, class_title, project_meta)
    label = process_label(label)
    print("Label processed.")
    g.api.annotation.update_label(figure_id, label)
    print("Label updated.")
