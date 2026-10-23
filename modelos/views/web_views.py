# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from modelos.services.catalog_service import get_site_context



class Index(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        if 'admin' in request.GET:
            return HttpResponseRedirect('/')
            
        context = get_site_context()
        return render(request, self.template_name, context)
