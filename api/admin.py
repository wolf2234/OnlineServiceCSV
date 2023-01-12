from django.contrib import admin
from .models import *

# Register your models here.


class SchemasInline(admin.TabularInline):
    model = Schemas
    extra = 1


@admin.register(DataSchemas)
class DataSchemasAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'modified')
    inlines = [SchemasInline]


@admin.register(Schemas)
class SchemasAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'order', 'data_schema')


