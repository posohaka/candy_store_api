from flask import Flask
from flask_restful import Api

from app import models
from app.models import db
from app.resources.courier import Couriers
from app.resources.order import AssignOrders, CompleteOrder, Orders
from app.services.data_validator import Validator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = models.get_db_url()
app.app_context().push()
db.init_app(app)
api = Api(app)

validator = Validator()

api.add_resource(
    Couriers,
    '/couriers',
    '/couriers/<int:courier_id>',
    resource_class_kwargs={'validator': validator}
)
api.add_resource(
    Orders,
    '/orders',
    resource_class_kwargs={'validator': validator}
)
api.add_resource(
    AssignOrders,
    '/orders/assign',
    resource_class_kwargs={'validator': validator}
)
api.add_resource(
    CompleteOrder,
    '/orders/complete',
    resource_class_kwargs={'validator': validator}
)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
