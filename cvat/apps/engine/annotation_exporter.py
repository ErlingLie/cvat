import pathlib
import json
import os.path as osp
from cvat.apps.dataset_manager.task import TaskData
from cvat.apps.dataset_manager.task import get_task_data
from cvat.apps.dataset_manager.annotation import AnnotationIR
from django.db import transaction
from django.conf import settings
from cvat.apps.engine.log import slogger
from django.utils import timezone


import zipfile
from tempfile import TemporaryDirectory

from cvat.apps.engine.models import Task, StatusChoice


def get_all_annotations(include_test):
    '''
    Dumps all annotation data to COCO format.
    '''
    annotations = {"annotations": [],
                    "images" : [],
                    "info" : {},
                    "licences":[],
                    "categories":[]}
    annotations["licences"].append({"name": "", "id":0, "url":""})
    annotations["info"] = {"date_created" : str(timezone.localtime().timestamp()),
                            "contributor" : "", "description" : "" , "url" : "", "version" : "",
                            "year" : ""}
    annotation_id = 1
    image_id = 0
    for task in Task.objects.all():
        # if task.is_test() and not include_test:
        #     continue
        # elif not task.is_test() and include_test:
        #     continue
        task_data = TaskData(AnnotationIR(get_task_data(task.id)),task)
        for frame_annotation in task_data.group_by_frame():
            # get frame info
            image_id += 1
            image_db = {}
            image_db["id"] = image_id #task.get_lobal_image_id(frame_nbmr)
            image_db["file_name"] = f"{image_id-1}.jpg"
            image_db["license"] = 0
            image_db["width"] = frame_annotation.width
            image_db["height"] = frame_annotation.height
            annotations["images"].append(image_db)
            # iterate over all shapes on the frame
            for shape in frame_annotation.labeled_shapes:
                label_id = task_data._get_label_id(shape.label)
                xtl = shape.points[0]
                ytl = shape.points[1]
                xbr = shape.points[2]
                ybr = shape.points[3]
                w = xbr-xtl
                h = ybr-ytl
                an_db = {"id" : annotation_id, "image_id" : image_id, "category_id" : label_id,
                "bbox" : [xtl, ytl, w, h], "area" : w*h, "iscrowd" : 0 }
                annotations["annotations"].append(an_db)
                annotation_id += 1
    return annotations


def get_json_path(include_test):
    label_name = "labels"
    if include_test:
        label_name = label_name + "_test"
    json_path = pathlib.Path(settings.DATA_ROOT, label_name + ".json")
    return str(json_path)


def should_update_annotation(include_test):
    json_path = get_json_path(include_test)
    tasks = Task.objects.all()
    if not osp.exists(json_path):
        return True
    #Find max time of newest updated task
    max_time = max(timezone.localtime(t.updated_date).timestamp() for t in tasks)
    archive_time = osp.getmtime(json_path)
    current_time = timezone.localtime().timestamp()
    #Update if max time is larger than archive time
    #And archive is more than eight hours old
    if(max_time > archive_time and current_time > archive_time + 8*60*60):
        print("Updating")
    else:
        print("Not updating")
    return max_time > archive_time and current_time > archive_time + 8*60*60


def get_annotation_filepath(include_test):
    json_path = get_json_path(include_test)
    if not should_update_annotation(include_test):
        return json_path
    annotations = get_all_annotations(include_test)
    with open(json_path, "w") as fp:
        json.dump(annotations, fp)
    return json_path


def annotation_file_ready(include_test):
    print("Running annotation_file_ready")
    return not should_update_annotation(include_test)
