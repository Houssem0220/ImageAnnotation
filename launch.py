from labelStudioEditor import *
from tqdm import tqdm
import os
import argparse
from pathlib import Path

from labelVideo import *

POLYGONS = 0
RLE = 1


def lire_urls_de_fichier(nom_fichier) -> list:
    """reads the URLs of the images to annotate and stocks them in a list

    Args:
        nom_fichier (String): name of the file containing the URLs of the images

    Returns:
        list: list of URLs
    """
    try:
        with open(nom_fichier, 'r') as f:
            urls = f.readlines()
            # Supprimer les espaces en début et en fin de ligne
            urls_propres = [url.strip() for url in urls]
            return urls_propres
    except FileNotFoundError:
        print(f"Le fichier '{nom_fichier}' est introuvable.")
        return []
    
def load_from_folder():
    config= ConfigParser()
    config.read("labelStudio.ini")
    config_data=config["DEFAULT"]
    media_folder_path = config_data["media_folder"]
    if len(media_folder_path)!=0:
        path = Path(media_folder_path)
        all_files = [str(file) for file in os.listdir(media_folder_path) if os.path.isfile(os.path.join(media_folder_path, file))]
        return all_files
    else :
        return []

    return all_files
def get_annotation_type():
    config= ConfigParser()
    config.read("labelStudio.ini")
    config_data=config["LABELING"]
    yolo_annotation_type = config_data["yolo_annotation_type"]

    if yolo_annotation_type=="r":
        annotation_type=RLE
    elif yolo_annotation_type=="p":
        annotation_type=POLYGONS

    return annotation_type
def label_image_list(project):
    """label the image list using yolo-v8 and generatea JSON file adapted to labelStudio inputs and imports them into the project

    Args:
        project_id (int): id of the project
    """
    annotation_type = get_annotation_type()
    
    list_images = lire_urls_de_fichier("images_sources.txt")
    list_images.extend(load_from_folder())
    for image in (list_images):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'}
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.mpeg', '.3gp'}
        
        # Extraire l'extension du chemin
        extension = image.lower().rsplit('.', 1)[-1]
        extension = '.' + extension  # Ajouter le point pour correspondre aux extensions dans les ensembles
        
        if extension in image_extensions:
            upload_one_image(project=project,PATH=image,type=annotation_type)
        elif extension in video_extensions:
            try:
                frames,paths=get_video_frames(PATH=image)

                for frame, path in tqdm(zip(frames,paths)):
                    upload_one_image(project=project,from_path=False,PATH=path,frame=frame,type=annotation_type)

            except Exception as e:
                print("Error")
                print(e)
        else:
            print("file type not supported")
        
def upload_one_image(project,type,from_path=True,PATH=None,frame=None):
    if from_path :
        assert PATH!=None, "ADD A PATH OF YOUR IMAGE"
        generate_formatter(URL=PATH, result_path="testJson.json",type=type,is_local=(PATH[:4]!="http"))
    else :
        assert frame!=None, "ADD A THE FRAME TO BE ANNOTATED"
        generate_formatter(URL=PATH,image=frame,result_path="testJson.json",type=type,is_local=(PATH[:4]!="http"))
    try:
        import_labels(project, "testJson.json")
    except Exception as e:
            print("Error occurred while launching project")
            print(e)

def annotate_images_in_new_project(name):
    """create a new labelStudio project and save the annotated images into it
    """
    client = start_label_studio_client()
    project = make_yolo_labeling_config(ls=client, project_name=name)
    label_image_list(project)

def annotate_images_in_an_existing_project(project_id):
    """connect to an existing  labelStudio project and save the annotated images into it
    """
    client = start_label_studio_client()
    project = open_existing_project(ls=client,id=project_id)
    label_image_list(project)

#python launch.py -id=106
#python launch.py -name=new
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch script")

    # Add arguments
    parser.add_argument('-id', type=int, help='ID of the project')
    parser.add_argument('-new', type=str, help='Name for the new project')

    # Parse the arguments
    args = parser.parse_args()

    # Custom validation to ensure only one argument is provided
    if (args.id is None and args.new is None) or (args.id is not None and args.new is not None):
        parser.error('Exactly one of -id or -name must be specified')

    # Access the arguments
    if args.id is not None:
        project_id = args.id
        annotate_images_in_an_existing_project(project_id)
    if args.new is not None:
        project_name = args.new
        annotate_images_in_new_project(project_name)
