# Automatic detection and tracking in videos for upload to CVAT

These tools are made to simplify the process of automatic detection with custom models for CVAT. The tool is divided into a three step process.
1. Run detection on all videos, and save detections to file.
2. Run tracking on detection outputs, and save tracks to file.
3. Produce CVAT xml format annotations from tracking outputs and upload corresponding videos and tracks to CVAT.

The tool works on folders, and it is important that the folders remain unchanged between each step of the process. In other words, do not add videos, remove videos or change video names in the video folder after running the detection script, but before running the upload script. That will lead to mismatch between annotations and videos.

## Detection script
The detection script is called **detect_on_videos.py**. It requires detectron2 installed. Normal usage goes like this:
```
python detect_on_videos.py video_directory output_directory --model_name path/to/detectron/model.pth --num_classes number_of_classes
```
Example:
```
python detect_on_videos.py traffic_videos detection_output --model_name models/traffic_model_final.pth --num_classes 4
```

The script will populate the output folder with one json file per input video. The video file is a dict of dicts on the format:
- Frame number
    - Class id : List of bboxes on form [x0, y0, x1, y1, score]

If you want to use a different detection model than detectron2 you must write your own Detection script that outputs jsons on the same format.

## Tracker script
The tracker script uses [Sort](https://github.com/abewley/sort). It takes the output from the detection script as input and runs the tracking algorithm on them. Normal usage goes like this:
```
python track_on_videos.py input_directory output_directory --num_classes number_of_classes
```
Example:
```
python track_on_videos.py detection_output tracker_output --num_classes 4
```

The output is a list of dicts where each dict includes all tracks for one class on the format:  *Track_id : List of BBoxes on format [x0, y0, x1, y1, frame_number]*

## Upload script
The upload script uploads all videos in the provided video folder to CVAT. Then it converts all the data in the provided tracker directory to CVAT style XML annotations, and uploads them to the corresponding videos. The XML annotations are not saved, and if one wishes to do so one must alter the script (altough it should not be too much work). The script requires that the file **labels.json** is present in the same directory as the script file. It also currently requires you to correctly set the class names inside the source code of the file.

Normal usage goes like this:
```
python upload_to_cvat.py input_video_directory input_tracker_directory cvat_username cvat_password
```

Example:
```
python upload_to_cvat.py traffic_videos tracker_output admin Password123
```
