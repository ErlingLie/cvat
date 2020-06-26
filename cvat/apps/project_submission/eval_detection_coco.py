from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


def calculate_detection_scores(detection_file, gt_file, leaderboard_data_amount: float = 0.3, annotation_type = "bbox"):
    '''
    Uses the COCO-api to calculate COCO metrics for bounding box detection or instance segmentation
    Args:
        detection_file (str): File path to detections on COCO json format
        gt_file        (str): File path to ground truth labels on COCO json format
        leaderboard_data_amount (float): Amount of total labeled data to use for calculation
        annotation_type (str): Either 'bbox' or 'segm'. Describes what type of task to test.
    '''
    coco_gt = COCO(gt_file.path)
    coco_dt = coco_gt.loadRes(detection_file.path)
    img_ids = sorted(coco_gt.getImgIds())
    img_ids = img_ids[0:int(leaderboard_data_amount*len(img_ids))]

    coco_eval = COCOeval(coco_gt,coco_dt,annotation_type)
    coco_eval.params.imgIds  = img_ids
    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()
    return coco_eval.stats



def compute_submission_map(submission_filefield,
                           solution_filefield,
                           leaderboard_data_amount: float = 0.3):
    total_result       = calculate_detection_scores(submission_filefield, solution_filefield, 1.0)
    leaderboard_result = calculate_detection_scores(submission_filefield, solution_filefield, leaderboard_data_amount)
    return total_result[0], leaderboard_result[0]

if __name__ == "__main__":
    print(calculate_detection_scores("test_files/detections.json", "test_files/annotations.json", .3))