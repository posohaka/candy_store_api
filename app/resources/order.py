import datetime

import flask
from flask import request
from flask_restful import Resource, marshal, fields

from app.models import Order, Courier, Delivery, db
from app.services import util
from app.services.util import Object

order_fields = {
    'id': fields.Integer(attribute='id')
}

order_list_fields = {
    'orders': fields.List(fields.Nested(order_fields))
}

order_complete_fields = {
    'order_id': fields.Integer(attribute='id')
}


class Orders(Resource):
    """
    Orders class used for HTTP requests related to creating orders
    :arg
    validator : Validator
        validate the json-body
    """

    def __init__(self, validator) -> None:
        super().__init__()
        self.validator = validator

    def post(self):
        """
        create orders by json of the request body
        :returns response with list new ids of orders and status 201
        :raises
            return response with status 400 if json-body is not validated
        """
        json_data = request.get_json(force=True)
        validate_result = self.validator.validate_post_order(json_data)
        if not validate_result[0]:
            if len(validate_result) == 2:
                return validate_result[1], 400
            else:
                return flask.Response(status=400)

        orders = []
        for data in json_data['data']:
            order = Order(
                id=data['order_id'],
                weight=round(data['weight'], 2),
                region=data['region'],
                delivery_hours=data['delivery_hours']
            )
            orders.append(order)
            db.session.add(order)

        db.session.commit()

        result = Object()
        result.orders = orders
        return marshal(result, order_list_fields), 201


class AssignOrders(Resource):
    """
    AssignOrders class used for HTTP requests related to assign orders
    :arg
        validator : Validator
            validate the json-body
    """

    def __init__(self, validator) -> None:
        super().__init__()
        self.validator = validator

    def post(self):
        """
        assign order on courier
        :return response with assigned orders on courier with status  200
        :raises
            return response with status 400 if json-body is not validated or courier with id not exists
        """
        json_data = request.get_json(force=True)
        validate_result = self.validator.validate_post_orders_assign(json_data)
        if not validate_result:
            return flask.Response(status=400)

        courier = Courier.query.filter_by(id=json_data['courier_id']).first()
        if not courier:
            return flask.Response(status=400)
        weight = util.get_weight_by_type(courier.courier_type)

        orders = db.session \
            .query(Order) \
            .filter(Order.region.in_(courier.regions),
                    Order.start_date.is_(None),
                    Order.finish_date.is_(None),
                    Order.courier_id.is_(None),
                    Order.weight <= weight) \
            .all()

        have_new_orders = False

        delivery = Delivery()
        for order in orders:
            start_date = datetime.datetime.now()
            if util.is_courier_has_time_for_order(courier, order):
                order.courier_id = courier.id
                order.start_date = start_date
                have_new_orders = True
                order.delivery = delivery

        if have_new_orders:
            courier.count_delivery += 1
            db.session.add(delivery)

        db.session.commit()
        result = Object()
        result.orders = db.session \
            .query(Order) \
            .filter(Order.start_date.isnot(None),
                    Order.finish_date.is_(None),
                    Order.courier_id == courier.id) \
            .all()
        return marshal(result, order_list_fields), 200


class CompleteOrder(Resource):
    """CompleteOrder class used for HTTP requests related to complete orders
    :arg
        validator : Validator
            validate the json-body
    """

    def __init__(self, validator) -> None:
        super().__init__()
        self.validator = validator

    def post(self):
        """
        complete order
        :return: response with id of completed order with status 200
        :raises
            return response with code 400 if json-body is not validated or courier or order is not found
        """
        json_data = request.get_json(force=True)
        validate_result = self.validator.validate_complete_order(json_data)
        if not validate_result:
            return flask.Response(status=400)
        courier = Courier.query.filter_by(id=json_data['courier_id']).first()
        if not courier:
            return flask.Response(status=400)
        order = db.session \
            .query(Order) \
            .filter(Order.id == json_data['order_id'],
                    Order.courier_id == courier.id,
                    Order.start_date.isnot(None)) \
            .first()
        if not order:
            return flask.Response(status=400)
        if order.finish_date is None:
            last_completed_order = db.session \
                .query(Order) \
                .filter(Order.courier_id == courier.id,
                        Order.delivery_id == order.delivery_id,
                        Order.finish_date.isnot(None)) \
                .order_by(Order.finish_date.desc()) \
                .first()

            start_date = order.start_date
            if last_completed_order:
                start_date = last_completed_order.finish_date

            order.finish_date = datetime.datetime.now()
            delivery_time = order.finish_date - start_date
            order.delivery_time = delivery_time.total_seconds()

        db.session.commit()
        return marshal(order, order_complete_fields), 200
