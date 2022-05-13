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


class Roles(Base):
    role_id = models.AutoField(db_column='RoleId', primary_key=True)
    role_name = models.CharField(max_length=50, null=False, blank=False, default="NA")
    code = models.CharField(db_column='Code', max_length=5, null=True, default=None)

    def __str__(self):
        return self.role_name

    class Meta:
        db_table = 'Roles'


class AccessPolicy(Base):
    logid = models.AutoField(db_column='LogId', primary_key=True)
    policyname = models.CharField(db_column='PolicyName', max_length=15)
    policy = models.TextField(db_column='Policy')
    type = models.CharField(db_column='Type', max_length=15, null=True, default=None)

    class Meta:
        db_table = "AccessPolicy"


class RolePolicies(Base):
    id = models.AutoField(db_column='id', primary_key=True)
    role_id = models.IntegerField(db_column='roles_id', null=True, blank=True, default=None)
    accesspolicy_id = models.IntegerField(db_column='accesspolicy_id', null=True, blank=True, default=None)

    class Meta:
        db_table = "Roles_policies"




