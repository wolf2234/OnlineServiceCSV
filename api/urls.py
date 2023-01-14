from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *

app_name = 'api'

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login_user'),
    path('list_data_schemas/', get_list_data_schemas, name='list_data_schemas'),
    path('data_schema/<int:pk>/', get_detail_data_schema, name='data_schema'),
    path('data_schema/create/', create_schema, name='create_schema'),
    path('data_schema/delete/<int:pk>/', delete_schema, name='delete_schema'),
    path('schema_field/delete/<int:pk>/', delete_schema_field, name='schema_field'),
    path('generate/csv/<int:pk>/', generate_csv, name='generate_csv'),
]

