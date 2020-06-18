import numpy as np
import sys
import time
import os
import json
import argparse

from sort.sort import Sort

def track_from_detections(detection_path, output_path, num_classes):
    '''
    Runs tracking on detections and saves result to a json file on form list(class_db)
    Where each class_db is on the form:
    - track id
        - list of bboxes on form [x0, y0, x1, y1, frame_nmbr]
    '''
    trackers = []
    #Instanciate one tracker per class
    for i in range(num_classes):
        tracker = Sort()
        trackers.append(tracker)

    with open(detection_path, "r") as json_file:
        data = json.load(json_file)
    tracks = [{} for i in range(num_classes)]
    for frame_nmbr, frame_detections in data.items():
        frame_nmbr = int(frame_nmbr)
        for class_id, class_detections in frame_detections.items():
            class_id = int(class_id)
            class_tracks = trackers[class_id].update(np.array(class_detections))
            for track in class_tracks: #Tracks are on form [x0, y0, x1, y1, id]
                if int(track[-1]) in tracks[class_id].keys():
                    tracks[class_id][int(track[-1])].append(track[:4].tolist() + [frame_nmbr])
                else:
                    tracks[class_id][int(track[-1])] = [track[:4].tolist() + [frame_nmbr]]

    with open(output_path, "w") as json_file:
        json.dump(tracks, json_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface for running detection on videos")
    parser.add_argument("input", type=str, help = "Directory for input jsons")
    parser.add_argument("output", type=str, help = "Directory for output jsons")
    parser.add_argument("--num_classes", default=1, type=int, help="Number of classes in dataset")
    args = parser.parse_args()

    if not os.path.exists(args.output):
            os.mkdir(args.output)
            print("Directory" , args.output ,  "Created ")
    detections = os.listdir(args.input)
    for detection in detections:
        output_path = os.path.join(args.output, detection)
        input_path = os.path.join(args.input, detection)
        print("Starting tracking on file: " + output_path)
        track_from_detections(input_path, output_path, args.num_classes)