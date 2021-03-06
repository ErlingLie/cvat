import json
import os.path as osp
from cvat.apps.dataset_manager.task import  get_task_data
from cvat.apps.dataset_manager.bindings import TaskData
from cvat.apps.dataset_manager.annotation import AnnotationIR
from django.conf import settings
from cvat.apps.engine.log import slogger
from django.utils import timezone
import zipfile


from cvat.apps.engine.models import Task, StatusChoice



def make_meta_json():
    annotations = {"annotations": [],
                    "images" : [],
                    "info" : {},
                    "licences":[],
                    "categories":[]}
    annotations["licences"].append({"name": "", "id":0, "url":""})
    annotations["info"] = {"date_created" : str(timezone.localtime()),
                            "contributor" : "", "description" : "" , "url" : "", "version" : "",
                            "year" : ""}
    return annotations

def get_all_annotations():
    '''
    Dumps all annotation data to COCO format.
    Updates both train and test data.
    '''
    train = make_meta_json()
    test  = make_meta_json()
    task_data = None
    annotation_id = 1
    for task in Task.objects.all():
        if task.status != StatusChoice.COMPLETED:
            continue
        task_data = TaskData(AnnotationIR(get_task_data(task.id)),task)
        for frame_nmbr, frame_annotation in enumerate(task_data.group_by_frame()):
            # get frame info
            image_id = task.get_global_image_id(frame_nmbr)
            image_db = {}
            image_db["id"] = image_id
            image_db["file_name"] = str(image_id) + ".jpg"
            image_db["license"] = 0
            image_db["width"] = frame_annotation.width
            image_db["height"] = frame_annotation.height
            if task.is_test():
                test["images"].append(image_db)
            else:
                train["images"].append(image_db)
            # iterate over all shapes on the frame
            for shape in frame_annotation.labeled_shapes:
                label_id = task_data._get_label_id(shape.label)
                xtl = shape.points[0]
                ytl = shape.points[1]
                xbr = shape.points[2]
                ybr = shape.points[3]
                w = xbr-xtl
                h = ybr-ytl
                an_db = {"id" :  annotation_id, "image_id" : image_id, "category_id" : label_id,
                "bbox" : [xtl, ytl, w, h], "area" : w*h, "iscrowd" : 0 }
                if task.is_test():
                    test["annotations"].append(an_db)
                else:
                    train["annotations"].append(an_db)
                annotation_id += 1
    if task_data != None:
        label_map = task_data._label_mapping
        for key, val in label_map.items():
            label_dict = {"id" : key, "name" : val.name, "supercategory" : "", "keypoints": [], "skeleton" : []}
            test["categories"].append(label_dict)
            train["categories"].append(label_dict)
    train_path, test_path = get_json_paths(True)
    _, empty_test_path = get_json_paths(False)
    with open(train_path, "w") as json_file:
        json.dump(train, json_file)
    with open(test_path, "w") as json_file:
        json.dump(test, json_file)
    test["annotations"] = []
    with open(empty_test_path, "w") as json_file:
        json.dump(test, json_file)


def get_json_paths(include_test):
    train_name = "labels_train.json"
    test_name = "labels_test.json" if include_test else "empty_test.json"
    train_path = osp.join(settings.DATA_ROOT, train_name)
    test_path = osp.join(settings.DATA_ROOT, test_name)
    return train_path, test_path

def get_zip_path(include_test):
    label_name = "labels_with_test.zip" if include_test else "labels.zip"
    return osp.join(settings.DATA_ROOT, label_name)

def should_update_annotation(include_test):
    zip_path = get_zip_path(include_test)
    if not osp.exists(zip_path):
        return True
    #Find max time of newest updated task
    tasks = Task.objects.all()
    max_time = max(timezone.localtime(t.updated_date).timestamp() for t in tasks)
    archive_time = osp.getmtime(zip_path)
    current_time = timezone.localtime().timestamp()
    #Update if max time is larger than archive time
    #And archive is more than eight hours old
    return max_time > archive_time and current_time > archive_time + 8*60*60


def get_annotation_filepath(include_test):
    zip_path = get_zip_path(include_test)
    if not should_update_annotation(include_test):
        return zip_path
    get_all_annotations()
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        train_path, test_path = get_json_paths(include_test)
        zip_file.write(train_path, osp.basename(train_path))
        zip_file.write(test_path, osp.basename(test_path))
    return zip_path


def annotation_file_ready(include_test):
    return not should_update_annotation(include_test)
