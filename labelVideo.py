import cv2
from ultralytics import YOLO
import os

def save_image(path, frame):
    # Extract directory from the given path
    directory = os.path.dirname(path)
    
    # Check if the directory exists
    if not os.path.exists(directory):
        # If it does not exist, create the directory
        os.makedirs(directory)
    
    # Save the image
    cv2.imwrite(path, frame)

def get_video_frames(PATH):
    # Load the YOLOv8 model
    model = YOLO('yolov8x-seg.pt')


    # Open the video file

    cap = cv2.VideoCapture(PATH)

    list_of_annotated_frames=[]
    list_of_paths=[]
    # Loop through the video frames
    i=0
    while cap.isOpened():

    # Read a frame from the video
        success, frame = cap.read()

        if success:
            i+=1
            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True)

            # Visualize the results on the frame
            list_of_annotated_frames.append(results)
            file_name_with_extension = os.path.basename(PATH)
    
            # Extraire le nom de fichier sans extension
            file_name, _ = os.path.splitext(file_name_with_extension)
            save_image(f"{os.path.dirname(PATH)}/{file_name}/{file_name}_frame{i}.jpg",frame)

            list_of_paths.append(f"{os.path.dirname(PATH)}/{file_name}/{file_name}_frame{i}.jpg")

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

        # Release the video capture object and close the display window
    cap.release()

    cv2.destroyAllWindows()

    return (list_of_annotated_frames,list_of_paths)
