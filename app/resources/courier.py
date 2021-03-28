import flask
from flask import request
from flask_restful import Resource, fields, marshal

from app.services.data_validator import Validator
from app.models import Courier, db, Order
from app.services import util
from app.services.util import Object

courier_fields = {
    'id': fields.Integer(attribute='id')
}

courier_list_fields = {
    'couriers': fields.List(fields.Nested(courier_fields))
}

patch_courier_fields = {
    'courier_id': fields.Integer(attribute='id'),
    'courier_type': fields.String,
    'regions': fields.List(fields.Integer),
    'working_hours': fields.List(fields.String)
}

courier_get_fields = {
    'courier_id': fields.Integer(attribute='id'),
    'courier_type': fields.String,
    'regions': fields.List(fields.Integer),
    'working_hours': fields.List(fields.String),
    'rating': fields.Float,
    'earnings': fields.Integer
}


class Couriers(Resource):
    """
    Couriers class uses for HTTP requests that are courier related
    :arg
    validator : Validator
        validate the json-body
    """

    def __init__(self, validator: Validator) -> None:
        super().__init__()
        self.validator = validator

    def post(self):
        """
        create couriers by json of the request body
        :returns response with ids of new couriers and status 201
        :raises
            return response with status 400 if json-body is not validated
        """
        json_data = request.get_json(force=True)
        validate_result = self.validator.validate_post_courier(json_data)
        if not validate_result[0]:
            if len(validate_result) == 2:
                return validate_result[1], 400
            else:
                return flask.Response(status=400)

        couriers = []
        for data in json_data['data']:
            courier = Courier(
                id=data['courier_id'],
                courier_type=data['courier_type'],
                regions=data['regions'],
                working_hours=data['working_hours']
            )
            couriers.append(courier)
            db.session.add(courier)

        db.session.commit()

        result = Object()
        result.couriers = couriers
        return marshal(result, courier_list_fields), 201

    def get(self, courier_id: int):
        """
        return courier with statistic by courier_id
        :param courier_id: int
        :returns response with courier by id and status 200
        :raises
            return response with status 400 if courier is not exists
        """
        courier = Courier.query.filter_by(id=courier_id).first()
        if not courier:
            return flask.Response(status=400)
        courier.rating = util.get_courier_rating(courier)
        courier.earnings = util.get_earnings(courier)

        return marshal(courier, courier_get_fields), 200

    def patch(self, courier_id):
        """
        return and update courier by courier_id
        :param courier_id: int
        :returns: response with updated courier by id and status 200
        :raises
            return response with status 400 if courier is not exists or json-body is not validated
        """
        json_data = request.get_json(force=True)
        validate_result = self.validator.validate_path_courier(json_data)
        if not validate_result:
            return flask.Response(status=400)
        courier = Courier.query.filter_by(id=courier_id).first()
        if not courier:
            return flask.Response(status=400)
        if 'courier_type' in json_data:
            courier.courier_type = json_data['courier_type']
        if 'regions' in json_data:
            courier.regions = json_data['regions']
        if 'working_hours' in json_data:
            courier.regions = json_data['working_hours']

        weight = util.get_weight_by_type(courier.courier_type)
        orders = db.session \
            .query(Order) \
            .filter(Order.courier_id == courier.id,
                    Order.start_date.isnot(None),
                    Order.finish_date.is_(None)) \
            .all()

        for order in orders:
            if order.weight > weight \
                    or order.region not in courier.regions \
                    or not util.is_courier_has_time_for_order(courier, order):
                order.start_date = None
                order.courier_id = None

        db.session.commit()

        return marshal(courier, patch_courier_fields), 200
