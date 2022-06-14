from django.db import models


# Create your models here.


class CustomDateTimeField(models.DateTimeField):
    def db_type(self, connection):
        return 'datetime'


class Base(models.Model):
    created_on = CustomDateTimeField(db_column='CreatedOn', auto_now_add=True)
    modified_on = CustomDateTimeField(db_column='ModifiedOn', auto_now=True)

    class Meta:
        abstract = True


class IndustryTypes(models.Model):
    id = models.IntegerField(db_column="id", primary_key=True)
    industry_type = models.CharField(db_column="IndustryType", max_length=300, null=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'IndustryTypes'