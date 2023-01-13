from django.urls import path, include
from .views import *

app_name = 'api'

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login_user'),
    path('list_data_schemas/', get_list_data_schemas, name='list_data_schemas'),
    path('data_schema/<int:pk>/', get_detail_data_schema, name='data_schema'),
    path('data_schema/create/', create_schema, name='create_schema'),
    path('generate/csv/<int:pk>/', generate_csv, name='generate_csv'),
]

