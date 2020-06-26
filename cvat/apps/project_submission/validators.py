import json
import os
from django.core.exceptions import ValidationError


def validate_json_formatted(filefield):
    try:
        l = json.loads(filefield.read().decode())
        if not isinstance(l, list):
            raise ValidationError('The outer JSON type must be a list')
        if len(l) == 0:
            raise ValidationError('Empty submission')
        expected_fields = set(['image_id', 'bounding_boxes'])
        expected_bbox_fields = set(['xmin', 'xmax', 'ymin', 'ymax','label'])

        for image_annotation in l:
            if not isinstance(image_annotation, dict):
                raise ValidationError('Invalid annotation JSON: List entries are not json')
            if not expected_fields.issubset(set(image_annotation.keys())):
                 raise ValidationError('Invalid annotation JSON: Entry keys not correct')
            if not isinstance(image_annotation['image_id'], int):
                raise ValidationError('Invalid annotation JSON: Missing image_id')
            if not isinstance(image_annotation['bounding_boxes'], list):
                raise ValidationError('Invalid annotation JSON: List of bounding_boxes missing')
            for bbox in image_annotation['bounding_boxes']:
                if not isinstance(bbox, dict):
                    raise ValidationError('Invalid annotation JSON: BBOX formatting not right')
                if not expected_bbox_fields.issubset(set(bbox.keys())):
                    raise ValidationError('Invalid annotation JSON, BBOX missing an expected key')
    except Exception as e:
        raise ValidationError('Expected a UTF-8 formatted JSON file. '+str(e))
