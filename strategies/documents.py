from datetime import datetime
from elasticsearch_dsl import (
    DocType, Date, Nested, Boolean, Object,
    Long, Integer, String, GeoPoint, Float,
    InnerObjectWrapper, Keyword, Text,
)


class Delta(InnerObjectWrapper):
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
    orderID = Text(fields={'raw': Keyword()})
    qty = Float()
    status = Text()
    comment = Text(fields={'raw': Keyword()})

    published = Boolean()
    created_at = Date()
    delta_series = Nested(Delta)

    class Meta:
        index = 'bitmex'

    def add_comment(self, author, content):
        self.comments.append(
          Comment(author=author, content=content, created_at=datetime.now()))

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)
