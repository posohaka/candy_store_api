import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_db_url() -> str:
    user_db = os.environ['POSTGRES_USER']
    password_db = os.environ['POSTGRES_PASSWORD']
    db_name = os.environ['POSTGRES_DB']
    db_port = os.environ['POSTGRES_PORT']
    return f"postgresql://{user_db}:{password_db}@postgres:{db_port}/{db_name}"


class Courier(db.Model):
    __tablename__ = 'couriers'
    id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(db.String(10))
    regions = db.Column(db.ARRAY(db.Integer))
    working_hours = db.Column(db.ARRAY(db.String(30)))
    orders = db.relationship('Order', backref='couriers', lazy=True)
    count_delivery = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f'<Courier {self.id}>'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer)
    region = db.Column(db.Integer)
    delivery_hours = db.Column(db.ARRAY(db.String(30)))
    courier_id = db.Column(db.Integer, db.ForeignKey('couriers.id'))
    start_date = db.Column(db.DateTime, default=None)
    finish_date = db.Column(db.DateTime, default=None)
    delivery_time = db.Column(db.Float, default=None)

    def __repr__(self) -> str:
        return f'<Order {self.id}>'
