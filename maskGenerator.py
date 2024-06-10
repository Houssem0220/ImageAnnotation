from ultralytics import YOLO
import numpy as np
import cv2
from brush import *

def load_model():
    """load yolo-v8 model 

    Returns:
        ultralytics.models.yolo.model.YOLO: yolo-v8 model
    """
    # Load a model
    model = YOLO('yolov8x-seg.pt')
    return model  # build a new model from YAML

def predict_image(model,URL):
    """predict image using yolo-v8

    Args:
        model (ultralytics.models.yolo.model.YOLO): model to use for prediction
        URL (String): URL of the image

    Returns:
        ultralytics.engine.results.Results : object containing the data of annotations predicted by the model
    """
    results = model(URL)  # predict on an image
    result=results[0]
    return result

def get_image_dimensions(result):
    """returns image dimensions

    Args:
        result (ultralytics.engine.results.Results) : object containing the data of annotations predicted by the model

    Returns:
        (int,int): height and width of the image 
    """
    width,height=result.orig_shape
    return height,width

def show_image(result):
    """displays image annotated. this function is used only for testing purposes.

    Args:
        result (ultralytics.engine.results.Results) : object containing the data of annotations predicted by the model

    """
    result.show()  # display to screen

def generate_masks_non_normalized(result):
    """generates masks non normalized

    Args:
        result (ultralytics.engine.results.Results) : object containing the data of annotations predicted by the model

    """
    masks_final=[mask.tolist() for mask in result.masks.xy]
    return masks_final

def generate_masks_normalized(mask_non_normalized,width,height):
    """normalize masks of polygons

    Args:
        mask_non_normalized (list): list of point coordinates non normalized
        width (int): image width
        height (int): image height

    Returns:
        list: list of point coordinates normalized 
    """
    masks_all=[]
    for mask_test in mask_non_normalized:
        new_mask=[]
        for sublist in mask_test:
                new_sublist = []
                for i, value in enumerate(sublist):
                    if i == 0:
                        new_value = (value / width) * 100  # Normalize with respect to 960
                    elif i == 1:
                        new_value = (value / height) * 100  # Normalize with respect to 500
                    else:
                        new_value = value  # Keep the value unchanged for other columns
                    new_sublist.append(new_value)
                new_mask.append(new_sublist)
        masks_all.append(new_mask)
    return masks_all

def generate_labels(result):
    """generate labels predicted by yolo model

    Args:
        result (ultralytics.engine.results.Results : object containing the data of annotations predicted by the model)

    Returns:
        list: list of labels predicted by yolo model
    """
    result_labels=[int(i) for i in list(result.boxes.cls)]
    return result_labels

def generate_entire_mask(result):
    img = np.copy(result.orig_img)
    myMasks=[]
    # Create binary mask
    for i in range(len(result.masks.xy)):
        b_mask = np.zeros(img.shape[:2], np.uint8)
    #  Extract contour result
        contour = result.masks.xy[i]
        #  Changing the type
        contour = contour.astype(np.int32)
        #  Reshaping
        contour = contour.reshape(-1, 1, 2)

        test = cv2.drawContours(b_mask,
                            [contour],
                            -1,
                            (255, 255, 255),
                            cv2.FILLED)
        myMasks.append(test)
    
    return myMasks


def generateRLE(masks):
    return [image2rle_edited(mask) for mask in masks]

