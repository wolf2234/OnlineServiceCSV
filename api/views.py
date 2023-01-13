from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.views.generic.base import View
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from OnlineServiceCSV.settings import MEDIA_ROOT
import os
import mimetypes
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
        column_name = request.POST.get('Column name')
        type = request.POST.get('Type')
        order = request.POST.get('Order')
        Schemas.objects.create(name=column_name, type=type, order=order, data_schema=data_schema)
        return HttpResponseRedirect(reverse('api:data_schema', args=(pk,)))
        # generate_csv(request.POST, pk)
    return render(request, 'api/data_schema.html', {'data_schema': data_schema,
                                                    'schema_columns': schema_columns,
                                                    'list_types': list_types})


def create_schema(request):
    list_types = [type_obj[1] for type_obj in CHOICES]
    if request.POST:
        name_schema = request.POST.get('Name')
        separator = request.POST.get('Column separator')
        column_name = request.POST.get('Column name')
        type = request.POST.get('Type')
        order = request.POST.get('Order')
        data_schema = DataSchemas.objects.create(title=name_schema, column_separator=separator)
        if column_name and type and order:
            Schemas.objects.create(name=column_name, type=type, order=order, data_schema=data_schema)
        return redirect('/api/list_data_schemas/')
    else:
        return render(request, 'api/data_schema.html', {'list_types': list_types})


def generate_csv(request, pk):
    data_schema = DataSchemas.objects.get(pk=pk)
    schema_columns = data_schema.schemas_set.all()
    filename = f"{data_schema.title}.csv"
    filepath = f"{MEDIA_ROOT}/{filename}"
    if schema_columns:
        names = [schema.name for schema in data_schema.schemas_set.all()]
        types = [schema.type for schema in data_schema.schemas_set.all()]
        orders = [schema.order for schema in data_schema.schemas_set.all()]
    else:
        names = ""
        types = ""
        orders = ""

    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='cp1251', newline="") as file:
            writer = csv.writer(file, delimiter=data_schema.column_separator)
            writer.writerow(
                    ['Column name', 'Type', 'Order']
            )
            if names and types and orders:
                for column_name, type_field, order in zip(names, types, orders):
                    writer.writerow(
                        [column_name, type_field, order]
                )
    else:
        with open(filepath, 'r') as f:
            data_file = f.read()
            with open(filepath, 'a', encoding='cp1251', newline="") as file:
                writer = csv.writer(file, delimiter=data_schema.column_separator)
                if names and types and orders:
                    for column_name, type_field, order in zip(names, types, orders):
                        if column_name in data_file:
                            continue
                        else:
                            writer.writerow(
                                [column_name, type_field, order]
                            )

    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(filepath, content_type=mime_type)
    response['Content-Disposition'] = f"attachment; filename={filename}"
    return response

# def generate_csv(schema_data, pk):
#     dict_schema_data = dict(schema_data)
#     name_schema = dict_schema_data.get('Name')[0]
#     separator = dict_schema_data.get('Column separator')[0]
#     names = dict_schema_data.get('Column name')
#     types = dict_schema_data.get('Type')
#     orders = dict_schema_data.get('Order')
#     print(dict_schema_data)
#     if not os.path.exists(f"{MEDIA_ROOT}/{name_schema}.csv"):
#         with open(f"{MEDIA_ROOT}/{name_schema}.csv", 'w', encoding='cp1251', newline="") as file:
#             writer = csv.writer(file, delimiter=separator)
#             writer.writerow(
#                 ['Column name', 'Type', 'Order']
#             )
#             for column_name, type_field, order in zip(names, types, orders):
#                 writer.writerow(
#                     [column_name, type_field, order]
#                 )
#     else:
#         with open(f"{MEDIA_ROOT}/{name_schema}.csv", 'a', encoding='cp1251', newline="") as file:
#             writer = csv.writer(file, delimiter=separator)
#             for column_name, type_field, order in zip(names, types, orders):
#                 writer.writerow(
#                     [column_name, type_field, order]
#                 )
#     return HttpResponseRedirect(reverse('api:data_schema', args=(pk,)))