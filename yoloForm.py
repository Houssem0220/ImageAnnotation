import json
from labeling import *
from fusion import *

active_labels = import_labels_from_config()[0]
names = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket',
         39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}


class JsonYoloFormatter:
    new_data = """{"value": {
            "points": #points#,
            "closed": true,
            "polygonlabels": [
              "#label#"
            ]},
            "from_name": "label",
            "to_name": "image",
            "type": "polygonlabels",
            "origin": "manual"},#newItem#"""
    new_data_rle = """{"value": {
            "format": "rle",
            "rle": #rle#,
            "closed": true,
            "brushlabels": [
              "#label#"
            ]},
            "from_name": "label2",
            "to_name": "image",
            "type": "brushlabels",
            "origin": "manual"},#newItem#"""

    def __init__(self, point_coordinates, labels, image_path, file_path="json_sample.txt", rle=[]):
        """creates a JsonYoloFormatter instance

        Args:
            point_coordinates (list): the coordinates of the the list of points of the mask
            labels (list): list of labels
            image_path (String): URL of the image
            file_path (str, optional): json file that will be edited. Defaults to "json_sample.txt".
        """
        self.point_coordinates = point_coordinates
        with open(file_path, 'r') as file:
            self.Json = file.read()
        self.labels = labels
        self.image_path = image_path
        self.rle = rle
        self.Json = self.Json.replace("#Image#", self.image_path)

    def save_to_file(self, file_path):
        """saves the Json file generated in the given path

        Args:
            file_path (String): path and name of the JSON file to save
        """
        if self.Json:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.Json)
            except IOError:
                print("Error occurred while saving to file.")
        else:
            print("No JSON data to save.")

    def get_label_from_fusion(self, id, dico_fusions, dico_ids):
        try:
            return dico_fusions[dico_ids[id]]
        except KeyError as e:
            return dico_ids[id]

    def format_json(self):
        """Generates the JSON of the labeled image using the given points and labels predicted by yolo-v8
        """
        assert len(self.labels) == len(self.point_coordinates)
        dico_fusions = get_fusion_dict()
        n = len(self.labels)
        for i in range(n):
            if self.get_label_from_fusion(self.labels[i], dico_fusions, names) in active_labels:
                self.Json = self.Json.replace("#newItem#", self.new_data)
                self.Json = self.Json.replace(
                    "#points#", str(self.point_coordinates[i]))
                self.Json = self.Json.replace(
                    "#label#", str(self.get_label_from_fusion(self.labels[i], dico_fusions, names)))

        self.Json = self.Json.replace(",#newItem#", "")

    def format_json_rle(self):
        n = len(self.labels)
        dico_fusions = get_fusion_dict()
        for i in range(n):
            if self.get_label_from_fusion(self.labels[i], dico_fusions, names)in active_labels:
                self.Json = self.Json.replace("#newItem#", self.new_data_rle)
                self.Json = self.Json.replace("#rle#", str(self.rle[i]))
                self.Json = self.Json.replace(
                    "#label#", str(self.get_label_from_fusion(self.labels[i], dico_fusions, names)))

        self.Json = self.Json.replace(",#newItem#", "")
