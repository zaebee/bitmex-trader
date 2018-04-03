# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.shortcuts import redirect
from django.views.generic.base import TemplateView


# from . models import Order


class View404(TemplateView):
    template_name = '404.html'


class MainPageView(TemplateView):
    template_name = 'mainpage.html'
