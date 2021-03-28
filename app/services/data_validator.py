import json
import os
import re

import jsonschema

from app.models import Courier, Order


def _load_schema(schema_name: str) -> dict:
    """
    load json-schema from directory schemas by name
    :param schema_name:
    :return:
        dict from file
    """
    with open(os.path.join(os.path.dirname(__file__), 'schemas', schema_name)) as f:
        return json.load(f)


def get_error_body(entity_name: str, entity_ids: list) -> dict:
    """
    return error-body if json-body is not validated
    :param entity_name:
    :param entity_ids:
    :return:
        error-body
    """
    return {
        "validation_error": {
            entity_name: entity_ids
        }
    }


def valid_time_list(time_ranges: [str]) -> bool:
    """
    validate list of time-range
    :param time_ranges:
    :return:
        True if list is corrected, False if not
    """
    for time_range in time_ranges:
        times = time_range.split("-")
        if len(times) != 2:
            return False
        if not (valid_time(times[0]) and valid_time(times[1])):
            return False

    return True


def valid_time(time_range: str) -> bool:
    """
    validate time-range
    :param time_range:
    :return:
        time-range is validated
    """
    regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    p = re.compile(regex)
    if time_range == "":
        return False
    m = re.search(p, time_range)

    if m is None:
        return False
    else:
        return True


class Validator:
    """
    Validator class used for validate json-body
    :arg
        courier_path_schema
        courier_post_schema
        order_post_schema
        data_schema
        post_orders_assign_schema
        complete_order_schema
    """
    def __init__(self) -> None:
        self.courier_path_schema = _load_schema("courier_path_schema.json")
        self.courier_post_schema = _load_schema("courier_post_schema.json")
        self.order_post_schema = _load_schema("order_post_schema.json")
        self.data_schema = _load_schema("data_schema.json")
        self.post_orders_assign_schema = _load_schema("orders_assign_schema.json")
        self.complete_order_schema = _load_schema("complete_order_schema.json")

    def validate_post_courier(self, instance):
        """
        validate json-body of post-request '/couriers'
        :param instance: json-body
        :return: True if json-body is validated, or False with error-body
        """
        try:
            jsonschema.validate(instance=instance, schema=self.data_schema)
        except jsonschema.exceptions.ValidationError:
            return False,
        error_entity_ids = []
        for entity in instance['data']:
            try:
                jsonschema.validate(instance=entity, schema=self.courier_post_schema)
            except jsonschema.exceptions.ValidationError:
                if 'courier_id' not in entity:
                    return False,
                error_entity_ids.append({'id': entity['courier_id']})
                continue
            entity_id = entity['courier_id']
            exists_entity = Courier.query.filter_by(id=entity_id).first()
            if exists_entity:
                error_entity_ids.append({'id': entity_id})
                continue
            if not valid_time_list(entity['working_hours']):
                error_entity_ids.append({'id': entity_id})

        if error_entity_ids:
            return False, get_error_body('couriers', error_entity_ids)

        return True,

    def validate_post_order(self, instance):
        """
        validate json-body of post-request '/orders'
        :param instance: json-body
        :return: True if json-body is validated, or False with error-body
        """
        try:
            jsonschema.validate(instance=instance, schema=self.data_schema)
        except jsonschema.exceptions.ValidationError:
            return False,
        error_entity_ids = []
        for entity in instance['data']:
            try:
                jsonschema.validate(instance=entity, schema=self.order_post_schema)
            except jsonschema.exceptions.ValidationError:
                if 'order_id' not in entity:
                    return False,
                error_entity_ids.append({'id': entity['order_id']})
                continue
            entity_id = entity['order_id']
            exists_entity = Order.query.filter_by(id=entity_id).first()
            if exists_entity:
                error_entity_ids.append({'id': entity_id})
                continue
            if not valid_time_list(entity['delivery_hours']):
                error_entity_ids.append({'id': entity_id})

        if error_entity_ids:
            return False, get_error_body('orders', error_entity_ids)

        return True,

    def validate_path_courier(self, instance):
        """
        validate json-body of path-request '/couriers/$courier_id'
        :param instance: json-body
        :return: True if json-body is validated, or False
        """
        try:
            jsonschema.validate(instance=instance, schema=self.courier_path_schema)
        except jsonschema.exceptions.ValidationError:
            return False

        return True

    def validate_post_orders_assign(self, instance):
        """
        validate json-body of post-request '/order/assign'
        :param instance: json-body
        :return: True if json-body is validated, or False
        """
        try:
            jsonschema.validate(instance=instance, schema=self.post_orders_assign_schema)
        except jsonschema.exceptions.ValidationError:
            return False

        return True

    def validate_complete_order(self, instance):
        """
        validate json-body of post-request '/order/complete'
        :param instance: json-body
        :return: True if json-body is validated, or False
        """
        try:
            jsonschema.validate(instance=instance, schema=self.complete_order_schema)
        except jsonschema.exceptions.ValidationError:
            return False

        return True
