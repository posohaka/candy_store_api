import numpy as nm

from app.models import Courier, Order, db

courier_types = {
    'foot': 10,
    'bike': 15,
    'car': 50
}

courier_factor = {
    'foot': 2,
    'bike': 5,
    'car': 9
}


class Object:
    pass


class TimeRange:
    def __init__(self, start, finish) -> None:
        self.start = start
        self.finish = finish

    def __ge__(self, other):
        return self.start <= other.start and self.finish >= other.finish


def is_courier_has_time_for_order(courier: Courier, order: Order) -> bool:
    """
    compare courier`s working-hours and order`s delivery-hours
    :param courier:
    :param order:
    :return: True if courier can accept order
    """
    courier_times = get_time_ranges(courier.working_hours)
    order_times = get_time_ranges(order.delivery_hours)
    for courier_time in courier_times:
        for order_time in order_times:
            if courier_time >= order_time:
                return True

    return False


def parse_time(time: str) -> int:
    """
    parse time-range
    :param time:
    :return: minutes
    """
    return int(time[:-3]) * 60 + int(time[-2:])


def get_time_ranges(ranges_str: [str]) -> [TimeRange]:
    """
    :param ranges_str:
    :return: list of time-ranges
    """
    time_ranges = []
    for range_str in ranges_str:
        start, finish = range_str.split('-')
        time_ranges.append(TimeRange(parse_time(start), parse_time(finish)))

    return time_ranges


def calculate_rating(time: float) -> float:
    """
    :param time:
    :return: rating
    """
    return (3600 - min(time, 3600)) / 3600 * 5


def get_courier_rating(courier: Courier) -> float:
    """
    :param courier:
    :return: courier rating
    """
    times_by_regions = []

    orders = db.session \
        .query(Order) \
        .filter(Order.courier_id == courier.id,
                Order.delivery_time.isnot(None)) \
        .all()
    delivery_times_by_region = {}
    for order in orders:
        if order.region not in delivery_times_by_region:
            delivery_times_by_region[order.region] = [order.delivery_time]
        else:
            delivery_times_by_region[order.region].append(order.delivery_time)
    for times in delivery_times_by_region.values():
        times_by_regions.append(nm.mean(times))
    time = float('inf')
    if times_by_regions:
        time = min(times_by_regions)

    return round(calculate_rating(time), 2)


def get_earnings(courier: Courier) -> int:
    """
    :param courier:
    :return: courier earnings
    """
    return 500 * courier.count_delivery * courier_factor[courier.courier_type]


def get_weight_by_type(courier_type: str) -> int:
    """
    :param courier_type:
    :return: weight by type
    """
    return courier_types[courier_type]
