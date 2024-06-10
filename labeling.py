from configparser import ConfigParser
from yoloForm import *
from fusion import *
colors = [
    "red", "green", "blue", "yellow", "orange", "purple", "cyan", "magenta", "lime", "pink",
    "teal", "lavender", "brown", "beige", "maroon", "olive", "coral", "navy", "grey", "silver",
    "crimson", "indigo", "tan", "gold", "violet", "aquamarine", "khaki", "turquoise", "orchid", "salmon",
    "skyblue", "peru", "plum", "darkorange", "thistle", "lightcoral", "cornflowerblue", "mediumaquamarine", "darkslategray", "mediumvioletred", "slateblue",
    "mediumspringgreen", "darkgoldenrod", "mediumorchid", "cadetblue", "rosybrown", "seagreen", "steelblue", "royalblue", "palevioletred", "slategray",
    "chartreuse", "paleturquoise", "forestgreen", "dodgerblue", "firebrick", "lightseagreen", "darkkhaki", "tomato", "dimgrey", "burlywood",
    "mediumseagreen", "darkorchid", "chocolate", "olivedrab", "powderblue", "indianred", "mediumslateblue", "darkseagreen", "saddlebrown", "darkslateblue",
    "peru", "cadetblue", "rosybrown", "seagreen", "steelblue", "royalblue", "palevioletred", "slategray", "chartreuse", "paleturquoise",
    "forestgreen", "dodgerblue", "firebrick", "lightseagreen", "darkkhaki", "tomato", "dimgrey", "burlywood", "mediumseagreen", "darkorchid"
]

names = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket',
         39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

def generate_label_studio_config(labels,text,type):
    config_template = '''
    <{} name="label{}" toName="image"
                 strokeWidth="3" pointSize="small"
                 opacity="0.9">'''
    label_template = '\n    <Label value="{}" background="{}"/>'
    end_template = '\n  </{}>'.format(type)

    labels_config = ''
    config_template=config_template.format(type,text)

    for label, color in zip(labels, colors):
        labels_config += label_template.format(label, color)

    return config_template + labels_config + end_template

def merge_label_configs(labels,polygon, rle,point):

    S="""<View>
    <Header value="Select label and click the image to start"/>
    <Image name="image" value="$image" zoom="true"/>"""
    if polygon:
        S+="""<Header value="Polygon Labeling"/>"""
        S+=generate_label_studio_config(labels,"","PolygonLabels")
    if rle:
        S+="""<Header value="Mask Labeling"/>"""
        S+=generate_label_studio_config(labels,"2","BrushLabels")
    if point :
        S+="""<Header value=" SAM point prompting"/>"""
        S+=generate_label_studio_config(["detect"],"3","KeyPointLabels")

    
    return S+"</View>"

def import_labels_from_config():

    config= ConfigParser()
    config.read("labelStudio.ini")
    config_data=config["LABELING"]
    
    LABELS = config_data["labels"].split(",")
    LABELS= [label.strip() for label in LABELS]
    
    list_fusion=list(set(get_fusion_dict().keys()))
    LABELS.extend(list(set(get_fusion_dict().values())))

    if "$YOLO$" in LABELS:
        LABELS.remove("$YOLO$")
        LABELS.extend(list(set(names.values()).difference(set(list_fusion))))

     
    RLE=bool(config_data["RLE"])

    POLYGON=bool(config_data["POLYGON"])

    POINT=bool(config_data["POINT"])
    
    return LABELS, POLYGON,RLE, POINT

def makeConfig():

    LABELS, POLYGON,RLE,POINT=import_labels_from_config()
    config=merge_label_configs(LABELS, polygon=POLYGON, rle=RLE,point=POINT)

    return config




