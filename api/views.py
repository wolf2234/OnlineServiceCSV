from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from OnlineServiceCSV.settings import MEDIA_ROOT
import os
import mimetypes
from .models import *
import csv

# Create your views here.
url_login = 'http://127.0.0.1:8000/admin/login/?next=/admin/'

# class LoginUser(View):
#
#     def get(self, request):
#         return render(request, 'api/login.html')
#
#     def post(self, request):
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('/api/list_data_schemas/')
#         else:
#             return render(request, 'api/login.html',
#                           {'error_message': 'Incorrect username and / or password.'})


@login_required(login_url=url_login)
def get_list_data_schemas(request):
    data_schemas = DataSchemas.objects.all()
    return render(request, 'api/list_data-schemas.html', {'data_schemas': data_schemas})


@login_required(login_url=url_login)
def get_detail_data_schema(request, pk):
    data_schema = DataSchemas.objects.get(pk=pk)
    schema_columns = list(data_schema.schemas_set.all())
    list_types = [type_obj[1] for type_obj in CHOICES]

    if request.POST:
        column_names = dict(request.POST).get('Column name')[0:-1]
        types = dict(request.POST).get('Type')[0:-1]
        orders = dict(request.POST).get('Order')[0:-1]

        data_columns = [(obj.name, obj.type, obj.order, obj) for obj in schema_columns]
        list_parameter = [(name, type_column, order_column) for name, type_column, order_column in zip(column_names, types, orders)]

        name_schema = request.POST.get('Name')
        separator = request.POST.get('Column separator')
        column_name = request.POST.get('Column name')
        type = request.POST.get('Type')
        order = request.POST.get('Order')

        if data_schema.title != name_schema:
            data_schema.title = name_schema
            data_schema.save()

        if data_schema.column_separator != separator:
            data_schema.column_separator = separator
            data_schema.save()

        for data_column, parameters in zip(data_columns, list_parameter):
            if data_column[0] != parameters[0]:
                data_column[3].name = parameters[0]

            if data_column[1] != parameters[1]:
                data_column[3].type = parameters[1]

            if data_column[2] != parameters[2]:
                data_column[3].order = parameters[2]

            data_column[3].save()

        if column_name and type and order:
            Schemas.objects.create(name=column_name, type=type, order=order, data_schema=data_schema)
            data_schema = DataSchemas.objects.get(pk=pk)
            data_schema.status = 'Ready'
            data_schema.save()
        return HttpResponseRedirect(reverse('api:data_schema', args=(pk,)))
        # generate_csv(request.POST, pk)
    return render(request, 'api/data_schema.html', {'data_schema': data_schema,
                                                    'schema_columns': schema_columns,
                                                    'list_types': list_types})


@login_required(login_url=url_login)
def create_schema(request):
    list_types = [type_obj[1] for type_obj in CHOICES]
    if request.POST:
        name_schema = request.POST.get('Name')
        separator = request.POST.get('Column separator')
        column_name = request.POST.get('Column name')
        type = request.POST.get('Type')
        order = request.POST.get('Order')
        data_schema = DataSchemas.objects.create(title=name_schema, column_separator=separator, status='Processing')
        if column_name and type and order:
            Schemas.objects.create(name=column_name, type=type, order=order, data_schema=data_schema)
            data_schema.status = 'Ready'
            data_schema.save()
        return redirect('/api/list_data_schemas/')
    else:
        return render(request, 'api/data_schema.html', {'list_types': list_types})


@login_required(login_url=url_login)
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


@login_required(login_url=url_login)
def delete_schema(request, pk):
    data_schema = DataSchemas.objects.get(pk=pk)
    data_schema.delete()
    return HttpResponseRedirect(reverse('api:list_data_schemas'))





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


@login_required(login_url=url_login)
def delete_schema_field(request, pk):
    schema = Schemas.objects.get(pk=pk)
    data_schema_id = schema.data_schema.id
    data_schema = DataSchemas.objects.get(pk=data_schema_id)
    schema.delete()
    if not data_schema.schemas_set.all():
        data_schema.status = 'Processing'
        data_schema.save()
    return HttpResponseRedirect(reverse('api:data_schema', args=(data_schema_id,)))
    # schema.delete()
