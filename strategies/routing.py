from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/trader/(?P<token_key>[^/]+)/(?P<token_secret>[^/]+)/$', consumers.StrategyConsumer),
]
