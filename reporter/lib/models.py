# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class ZeusQueryTask(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    status = models.IntegerField(blank=True, null=True)
    paused = models.IntegerField(blank=True, null=True)
    dimension = models.CharField(max_length=1024, blank=True)
    metric = models.CharField(max_length=1024, blank=True)
    filter = models.CharField(max_length=1024, blank=True)
    order = models.CharField(max_length=1024, blank=True)
    tablename = models.CharField(max_length=1024, blank=True)
    limit = models.IntegerField(blank=True, null=True)
    arguments = models.CharField(max_length=1024, blank=True)
    start_dt = models.IntegerField(blank=True, null=True)
    end_dt = models.IntegerField(blank=True, null=True)
    create_time = models.IntegerField(blank=True, null=True)
    parent_task_ids = models.CharField(max_length=45, blank=True)
    class Meta:
        managed = False
        db_table = 'zeus_query_task'
	app_label = 'zeus_query_task'

