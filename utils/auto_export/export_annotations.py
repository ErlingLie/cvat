import argparse
import os
import json
import subprocess
from datetime import datetime
import time
import zipfile

def get_tasks(username, password):
    response = subprocess.check_output([
            "../cli/cli.py",
            "--auth",
            username+":"+password,
            "ls"])
    response_str = response.decode("utf-8")
    tasks = [int(task.split(",")[0]) for task in response_str.strip().split("\n")]
    return tasks


def get_annotation_jsons(username, password, out_path):
    for task in tasks:
        response = subprocess.check_output([
            "../cli/cli.py",
            "--auth",
            username+":"+password,
            "dump" , str(task), os.path.join(out_path, f"annotations/{task}.zip"), "--format", "COCO 1.0"])
        with zipfile.ZipFile(os.path.join(out_path, f"annotations/{task}.zip"), "r") as f:
            f.extractall(".")
        os.rename(os.path.join(out_path, "annotations/instances_default.json"), os.path.join(out_path, f"annotations/{task}.json"))
        os.remove(os.path.join(f"annotations/{task}.zip"))


def merge_annotations(output_path,tasks, segment_length):
    '''
    Sort of a proof of concept of how annotations may be merged.
    Assume no overlap between video segments
    Assume frames are saved as 000000.jpg -> nnnnnn.jpg sequentially according to task id
    Args:
        segment_length (int): Number of fps for each segment
    '''
    merged_annotations = {"annotations": [], "images" : [], "categories": [], "licenses" : []}
    id_cnt = 1
    for task in tasks:
        with open(os.path.join(out_path, f"annotations/{task}.json"), "r") as json_file:
            db = json.load(json_file)
        for im in db["images"]:
            im["id"] += segment_length*task #Global ID number of total frames up untill now + current id
            im["filename"] = str(im["id"]-1).zfill(6) + ".jpg"
            merged_annotations["images"].append(im)
        for annotation in db["annotations"]:
            annotation["image_id"] += segment_length*task
            annotation["id"] = id_cnt
            id_cnt += 1
            merged_annotations["annotations"].append(annotation)
    merged_annotations["categories"] = db["categories"]
    merged_annotations["licenses"] = db["licenses"]
    with open(os.path.join(out_path, "all_annotations.json"), "w") as json_file:
        json.dump(merged_annotations, json_file)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracting annotation data")
    parser.add_argument("username", type=str, help = "Username")
    parser.add_argument("password", type=str, help = "Password")
    parser.add_argument("--out_path", type=str, default=".")
    args = parser.parse_args()
    username = args.username
    password = args.password
    out_path = args.out_path
    tasks = get_tasks(username, password)

    if not os.path.exists("annotations"):
            os.mkdir("annotations")

    get_annotation_jsons(username, password, out_path)
    merge_annotations(out_path, tasks, 20*35)


