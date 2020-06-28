import json
import os
from django.core.exceptions import ValidationError


def validate_json_formatted(filefield):
    try:
        l = json.loads(filefield.read().decode())
        expected_fields = set(["image_id", "category_id", "bbox", "score"])
        if not isinstance(l, list): #Most likely GT solution file
            l = l["annotations"]
            expected_fields.remove("score")
        if len(l) == 0:
            raise ValidationError("Empty submission")
        for annotation in l:
            if not isinstance(annotation, dict):
                raise ValidationError("Invalid annotations JSON: List entries are not dicts")
            if not expected_fields.issubset(set(annotation.keys())):
                raise ValidationError("Invalid annotation JSON: Entry keys are not correct")
            if not isinstance(annotation['image_id'], int):
                raise ValidationError('Invalid annotation JSON: Missing image_id')
            if not isinstance(annotation['bbox'], list):
                raise ValidationError('Invalid annotation JSON: List of bounding_boxes missing')
            if not len(annotation["bbox"]) == 4:
                raise ValidationError("Invalid annotation JSON: Bounding box list not of length 4")
    except Exception as e:
        raise ValidationError('Expected a UTF-8 formatted JSON file. '+str(e))
