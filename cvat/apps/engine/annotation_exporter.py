import json
import os.path as osp
from cvat.apps.dataset_manager.task import  get_task_data
from cvat.apps.dataset_manager.bindings import TaskData
from cvat.apps.dataset_manager.annotation import AnnotationIR
from django.conf import settings
from cvat.apps.engine.log import slogger
from django.utils import timezone



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
    print(annotations["info"])
    return annotations

def get_all_annotations():
    '''
    Dumps all annotation data to COCO format.
    Updates both train and test data.
    '''
    train = make_meta_json()
    test  = make_meta_json()

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
            image_db["file_name"] = f"{image_id-1}.jpg"
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
    train_path = get_json_path(False)
    test_path = get_json_path(True)
    with open(train_path, "w") as json_file:
        json.dump(train, json_file)
    with open(test_path, "w") as json_file:
        json.dump(test, json_file)


def get_json_path(include_test):
    label_name = "labels"
    if include_test:
        label_name = label_name + "_test"
    json_path = osp.join(settings.DATA_ROOT, label_name + ".json")
    return json_path


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
    return max_time > archive_time and current_time > archive_time + 8*60*60


def get_annotation_filepath(include_test):
    json_path = get_json_path(False)
    zip_path = json_path.split(".")[0] + ".zip"
    if not should_update_annotation(include_test):
        return zip_path if include_test else json_path
    get_all_annotations()
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        zip_file.write(json_path, osp.basename(json_path))
        test_path = get_json_path(True)
        zip_file.write(test_path, osp.basename(test_path))
    return zip_path if include_test else json_path


def annotation_file_ready(include_test):
    return not should_update_annotation(include_test)
