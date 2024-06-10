from maskGenerator import *
from yoloForm import *
from label_studio_sdk import Client, Project
#from label_studio_sdk._legacy import Project
import json
from brush import *
from labeling import *
from configparser import ConfigParser

POLYGONS=0
RLE=1

def generate_formatter(URL,result_path,type=POLYGONS,is_local=False,image=None):
    """generates JsonYoloFormatter for a given image and save the result of annotation

    Args:
        URL (String): URL of the image to anotate
        result_path (String): name of the Json File to save the result of annotation
    """
    if image== None:
        
        model=load_model()
        image_predicted=predict_image(model,URL)

    else : 
        image_predicted=image[0]

    width,height=get_image_dimensions(image_predicted)
    point_coordinates=generate_masks_normalized(generate_masks_non_normalized(image_predicted),width,height)
    labels=generate_labels(image_predicted)

    #Generating RLE
    rle=generateRLE(generate_entire_mask(image_predicted))
    if(is_local):
        config= ConfigParser()
        config.read("labelStudio.ini")
        config_data=config["DEFAULT"]
        document_root = Path(config_data["root_folder"])
        relative_path = str(Path(URL).relative_to(document_root))
        
        config= ConfigParser()
        config.read("labelStudio.ini")
        config_data = config["DEFAULT"]
        LABEL_STUDIO_URL = config_data["LABEL_STUDIO_URL"]

        formatter=JsonYoloFormatter(point_coordinates=point_coordinates,image_path=LABEL_STUDIO_URL+"/data/local-files/?d="+relative_path,labels=labels,rle=rle)        
    else:
        formatter=JsonYoloFormatter(point_coordinates=point_coordinates,image_path=URL,labels=labels,rle=rle)
    if type== POLYGONS:
        formatter.format_json()
    elif type==RLE:
        formatter.format_json_rle()
    formatter.save_to_file(result_path)

def start_label_studio_client():
    """start labelstudio client using the confi file

    Returns:
        Client: labelstudio client
    """
    print("Starting Label Studio client...")

    config= ConfigParser()
    config.read("labelStudio.ini")
    config_data=config["DEFAULT"]
    LABEL_STUDIO_URL = config_data["LABEL_STUDIO_URL"]
    API_KEY = config_data["API_KEY"]
    mail=config_data["mail"]

    with open("json_sample_raw.txt", 'r') as file:
            json_configuration = file.read()

    json_configuration=json_configuration.replace("#mail#",mail)
    
    with open("json_sample.txt", 'w') as file:
        file.write(json_configuration)

    # Initialize the Label Studio client
    ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
    
    return ls

def make_yolo_labeling_config(ls,project_name):
    """adds the labeling configuration to Label Studio Project

    Args:
        ls (Clinet): label studio client
        project_name (String): name of the project
    """

    project = ls.start_project(
    title=project_name,
    label_config=makeConfig()
)
    return project

def open_existing_project(ls,id):
    """runs an instance of an existing project using its id

    Args:
        ls (Client): label studio Client
        id (int): id of the project

    Returns:
        _type_: _description_
    """
    print("Opening project ",str(id))
    project = Project.get_from_id(ls, id)
    project.update_params()
    return project

def import_labels(project,path):
    """imports labels from the Json file into the project

    Args:
        project (Project): label studio project
        path (String): path of the Json file
    """
    with open(path, "r") as f:
        annotations = json.load(f)
    project.import_tasks(annotations)

from pathlib import Path
import os



