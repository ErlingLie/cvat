import xml.etree.ElementTree as ET
import xml.dom.minidom
import argparse
import os
import json
import subprocess
from datetime import datetime
import time

def insert_leaf(parent, name, text):
    sub = ET.SubElement(parent, name)
    sub.text = text

def insert_labels(parent, labels):
    for label_name in labels:
        label = ET.SubElement(parent, "label")
        insert_leaf(label, "name", label_name)
        insert_leaf(label, "attributes", "")

def insert_tracks_from_list(parent, data, labels):
    for i, track_class in enumerate(data):
        if len(track_class.keys()) == 0:
            continue
        for track_id, bboxes in track_class.items():
            track_node = ET.SubElement(parent, "track",\
                        {"id": str(track_id), "label" : labels[i]})
            for j, frame in enumerate(bboxes):
                xtl, ytl, xbr, ybr = frame[:4]
                frame_nmbr  = frame[4] - 1
                outside = "1" if (j == len(bboxes) - 1) else "0"
                ET.SubElement(track_node, "box", {"frame": str(frame_nmbr),\
                                            "xtl": str(xtl),
                                            "ytl": str(ytl),
                                            "xbr": str(xbr),
                                            "ybr": str(ybr),
                                            "outside": outside,
                                            "occluded": "0",
                                            "keyframe": "1"})

def make_meta_information(video_length, labels):
    annotations = ET.Element('annotations')
    version = ET.SubElement(annotations, "version")
    version.text = "1.0"
    meta = ET.SubElement(annotations, "meta")
    task = ET.SubElement(meta, "task")
    insert_leaf(task, "id", "1")
    insert_leaf(task, "name", "segmentation")
    insert_leaf(task, "size", str(video_length))
    insert_leaf(task, "overlap", "0")
    insert_leaf(task, "bugtracker", "")
    insert_leaf(task, "flipped", "False")
    now = datetime.now()
    insert_leaf(task, "created", now.strftime("%Y-%m-%d %H:%M:%S.%f") + "+00:00")
    insert_leaf(task, "updated", now.strftime("%Y-%m-%d %H:%M:%S.%f") + "+00:00")
    insert_labels(task, labels)
    insert_leaf(task, "segments", "")
    owner = ET.SubElement(task, "owner")
    insert_leaf(owner, "username", "admin")
    insert_leaf(owner, "email", "")
    return annotations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface for running detection on videos")
    parser.add_argument("input_videos", type=str, help = "Directory for input videos")
    parser.add_argument("input_tracks", type=str, help = "Directory for output jsons")
    parser.add_argument("username", type=str, help = "Username")
    parser.add_argument("password", type=str, help = "Password")
    args = parser.parse_args()
    classes = ["vehicle", "person", "sign", "cyclist"]
    videos = os.listdir(args.input_videos)
    tracks = os.listdir(args.input_tracks)
    username = args.username
    password = args.password
    task_count = 1
    ids = []
    videos.sort()

    for video in videos:
        response = subprocess.check_output([
            "../cli/cli.py",
            "--auth",
            username+":"+password,
            "create",
            "task_"+str(task_count)+"_"+video,
            "--labels",
            "labels.json",
            "local",
            os.path.join(args.input_videos, video)])
        task_count += 1
        print(response)
        ids.append(int(response.split()[3]))
        print("Sleeping 60 seconds")
        time.sleep(60)

    tracks.sort()
    if tracks[0].split(".")[-1] == "json":
        for i, track_file in enumerate(tracks):
            print("Sleeping 40")
            time.sleep(40)
            annotations = make_meta_information(2000, classes )
            with open(os.path.join(args.input_tracks, track_file), "r") as json_file:
                track_data = json.load(json_file)
            print("Making xml file from " + track_file)
            insert_tracks_from_list(annotations, track_data, classes)
            mydata = ET.tostring(annotations, encoding="unicode")
            mydata = xml.dom.minidom.parseString(mydata)
            with open("Temp.xml", "w") as myfile:
                myfile.write(mydata.toprettyxml())
            print(subprocess.check_output([
                "../cli/cli.py",
                "--auth",
                username+":"+password,
                "upload",
                str(ids[i]),
                "Temp.xml"]))
    elif tracks[0].split(".")[-1] == "xml":
        for i, track_file in enumerate(tracks):
            print("Sleeping 5")
            time.sleep(5)
            print(subprocess.check_output([
                "../cli/cli.py",
                "--auth",
                username+":"+password,
                "upload",
                str(ids[i]),
                os.path.join(args.input_tracks, track_file)]))
