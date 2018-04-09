from datetime import datetime
from elasticsearch_dsl import (
    DocType, Date, Nested, Boolean, Object,
    Long, Integer, String, GeoPoint, Float,
    InnerObjectWrapper, Keyword, Text,
)


class Delta(InnerObjectWrapper):
    orderID = Text(fields={'raw': Keyword()})
    symbol = Text(fields={'raw': Keyword()})
    side = Text(fields={'raw': Keyword()})

    enterPrice = Float()
    exitPrice = Float()
    basis = Float()
    average_rate = Float()
    created_at = Date()

    def age(self):
        return datetime.now() - self.created_at

    def points(self):
        return self.exitPrice - self.enterPrice


class Order(DocType):

    comment = Text(fields={'raw': Keyword()})
    status = Text()
    qty = Float()

    published = Boolean()
    created_at = Date()
    delta_series = Nested(Delta)

    class Meta:
        index = 'bitmex'

    def add_delta(self, **kwargs):
        self.delta_series.append(
            Delta(created_at=datetime.now(), **kwargs)
        )

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)
