import requests
import supervisely as sly
from typing import List, Dict
from pprint import pprint

API_TOKEN = (
    "ZWUoP49L9V9EGe352a2AHW8fhwmHT3BKM34SINWJ7jsFLdfJ2BjGvQrzR"
    "qiIqOFfVQ4pFRomDYFNI8xQLmb3dvRutRi4KkOqFkPGkrhPeKGh3wiNJIdT0vDJPnbzy0Tm"
)

# api = sly.Api(server_address="http://65.108.69.24:8088", token=API_TOKEN)

# ABSOLUTE_PATH = os.path.dirname(os.path.realpath(__file__))
# SAVE_DIR = os.path.join(ABSOLUTE_PATH, "data")
# sly.fs.mkdir(SAVE_DIR, remove_content_if_exists=True)
# JSON_SAVE_DIR = os.path.join(SAVE_DIR, "json")
# LABEL_SAVE_DIR = os.path.join(SAVE_DIR, "label")
# sly.fs.mkdir(JSON_SAVE_DIR, remove_content_if_exists=True)
# sly.fs.mkdir(LABEL_SAVE_DIR, remove_content_if_exists=True)

# TEAM_ID = 96
# WORKSPACE_ID = 148
# PROJECT_ID = 569
# # DATASET_ID = 986
# IMAGE_ID = 33979
# FIGURE_ID = 614776

# CLASS_TITLES = {
#     "bitmap": "tkot-masks",
#     "polygon": "tkot-polygon",
#     "polyline": "tkot-line",
#     "bbox": "tkot-bbox",
#     "point": "tkot-point",
# }

# project_meta = sly.ProjectMeta.from_json(api.project.get_meta(PROJECT_ID))
# image_np = api.image.download_np(IMAGE_ID)


def get_figure_by_id(
    figure_id: int, class_title: str, project_meta: sly.ProjectMeta
) -> sly.Label:
    response = requests.get(
        "http://65.108.69.24:8088/public/api/v3/figures.info",
        params={"id": figure_id, "decompressBitmap": False},
        headers={"x-api-key": API_TOKEN},
    ).json()

    response["classTitle"] = class_title
    geometry = response.pop("geometry")
    response.update(geometry)

    tags = get_figure_tags(figure_id)
    response["tags"] = tags

    return sly.Label.from_json(response, project_meta)


def get_figure_tags(figure_id: int) -> List[Dict]:
    response = requests.get(
        "http://65.108.69.24:8088/public/api/v3/figures.tags.list",
        params={"id": figure_id},
        headers={"x-api-key": API_TOKEN},
    ).json()

    return response or []


def edit_label(label: sly.Label) -> sly.Label:
    """Debug function, which recieves bitmap sly.Label and edits it."""
    return label.translate(100, 100)


def update_figure(figure_id: int, label: sly.Label):
    """Updates figure on server"""
    json_data = label.to_json()
    json_data["id"] = figure_id

    shape = json_data.get("shape")

    geometry = json_data.pop(shape)

    if "origin" in geometry:
        geometry["origin"] = [0, 0]

    json_data["geometry"] = {
        shape: geometry,
    }

    pprint(json_data)

    response = requests.put(
        "http://65.108.69.24:8088/public/api/v3/figures.editInfo",
        headers={"x-api-key": API_TOKEN},
        json=json_data,
    )

    print(response.status_code)
    print(response.json())


# def save_label(image_np: np.ndarray, label: sly.Label, save_path: str):
#     image_copy = image_np.copy()
#     label.draw(image_copy)
#     sly.image.write(save_path, image_copy)


# BEFORE_EDIT_SAVE_PATH = os.path.join(SAVE_DIR, "before_edit.png")
# BEFORE_EDIT_JSON_SAVE_PATH = os.path.join(SAVE_DIR, "before_edit.json")
# AFTER_EDIT_SAVE_PATH = os.path.join(SAVE_DIR, "after_edit.png")
# AFTER_EDIT_JSON_SAVE_PATH = os.path.join(SAVE_DIR, "after_edit.json")


# label = get_figure_by_id(FIGURE_ID, CLASS_TITLE, project_meta)

# save_label(image_np, label, BEFORE_EDIT_SAVE_PATH)
# sly.json.dump_json_file(label.to_json(), BEFORE_EDIT_JSON_SAVE_PATH)

# label = edit_label(label)

# save_label(image_np, label, AFTER_EDIT_SAVE_PATH)
# sly.json.dump_json_file(label.to_json(), AFTER_EDIT_JSON_SAVE_PATH)

# update_figure(FIGURE_ID, label)
# res_save_path = os.path.join(LABEL_SAVE_DIR, f"{FIGURE_ID}.json")
# sly.json.dump_json_file(label.to_json(), res_save_path)
# print(type(label))


# for label in ann.labels:
#     label: sly.Label
#     save_path = os.path.join(LABEL_SAVE_DIR, f"{label.geometry.name()}.json")
#     sly.json.dump_json_file(label.to_json(), save_path)

# json_label_path = "/Users/iwatkot/Documents/Supervisely/labeling-tool-template/src/data/json/614776.json"
# label_label_path = "/Users/iwatkot/Documents/Supervisely/labeling-tool-template/src/data/label/bitmap.json"

# figure = sly.json.load_json_file(json_label_path)
# label = sly.json.load_json_file(label_label_path)

# figure_tags = get_figure_tags(FIGURE_ID)


# def compare_dicts(dict1, dict2):
#     """Returns keys, that are in dict1, but not in dict2"""
#     return set(dict1.keys()) - set(dict2.keys())


# diff = compare_dicts(label, figure)
# print(diff)

# label = sly.Label.from_json(figure, project_meta)
# print(label.geometry.name())
