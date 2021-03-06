from cvat.apps.engine.frame_provider import FrameProvider
from cvat.apps.dataset_manager.task import  get_task_data
from cvat.apps.dataset_manager.bindings import TaskData
from cvat.apps.dataset_manager.annotation import AnnotationIR
from tempfile import TemporaryDirectory
from django.conf import settings
import PIL
from cvat.apps.dataset_manager.util import make_zip_archive
import os

from cvat.apps.engine.models import Task


def get_image_zip_path():
    return os.path.join(settings.DATA_ROOT, "images" + ".zip")

def get_all_images():
    '''
    Save all images to zip file.
    '''
    with TemporaryDirectory() as temp_dir:
        os.mkdir(os.path.join(temp_dir,"train"))
        os.mkdir(os.path.join(temp_dir, "test"))
        for task in Task.objects.all():
            frame_provider = FrameProvider(task.data)
            frames = frame_provider.get_frames(quality=frame_provider.Quality.ORIGINAL,
                                            out_type=frame_provider.Type.PIL)
            for frame_nmbr, frame in enumerate(frames):
                file_name =  str(task.get_global_image_id(frame_nmbr)) + ".jpg"
                sub_folder = "test" if task.is_test() else "train"
                path_name = os.path.join(temp_dir, sub_folder, file_name)
                frame[0].save(path_name)
        dest_path = get_image_zip_path()
        make_zip_archive(temp_dir, dest_path)
    return dest_path


if __name__ == "__main__":
    get_all_images()