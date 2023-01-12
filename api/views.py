from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse

import os
from pathlib import Path
from .models import *
import csv

# Create your views here.


class LoginUser(View):

    def get(self, request):
        return render(request, 'api/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'api/index.html')
        else:
            return render(request, 'api/login.html',
                          {'error_message': 'Incorrect username and / or password.'})


def get_list_data_schemas(request):
    data_schemas = DataSchemas.objects.all()
    return render(request, 'api/list_data-schemas.html', {'data_schemas': data_schemas})


def get_detail_data_schema(request, pk):
    data_schema = DataSchemas.objects.get(pk=pk)
    schema_columns = list(data_schema.schemas_set.all())
    list_types = [type_obj[1] for type_obj in CHOICES]
    if request.POST:
        generate_csv(request.POST, pk)
    return render(request, 'api/data_schema.html', {'data_schema': data_schema,
                                                    'schema_columns': schema_columns,
                                                    'list_types': list_types})

def generate_csv(schema_data, pk):
    dict_schema_data = dict(schema_data)
    name_schema = dict_schema_data.get('Name')[0]
    separator = dict_schema_data.get('Column separator')[0]
    names = dict_schema_data.get('Column name')
    types = dict_schema_data.get('Type')
    orders = dict_schema_data.get('Order')
    if not os.path.exists(f"{os.path.join(Path(__file__).resolve().parent.parent, 'media')}/{name_schema}.csv"):
        with open(f"{os.path.join(Path(__file__).resolve().parent.parent, 'media')}/{name_schema}.csv", 'w', encoding='cp1251', newline="") as file:
            writer = csv.writer(file, delimiter=separator)
            writer.writerow(
                ['Column name', 'Type', 'Order']
            )
            for column_name, type_field, order in zip(names, types, orders):
                writer.writerow(
                    [column_name, type_field, order]
                )
    else:
        with open(f"{os.path.join(Path(__file__).resolve().parent.parent, 'media')}/{name_schema}.csv", 'a', encoding='cp1251', newline="") as file:
            writer = csv.writer(file, delimiter=separator)
            for column_name, type_field, order in zip(names, types, orders):
                writer.writerow(
                    [column_name, type_field, order]
                )
    return HttpResponseRedirect(reverse('api:data_schema', args=(pk,)))