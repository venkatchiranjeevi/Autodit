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


class Users(models.Model):
    userid = models.AutoField(db_column='UserId', primary_key=True)
    mobnmbr = models.CharField(db_column='MobNmbr', max_length=20, null=True, blank=True, unique=True)
    email = models.EmailField(db_column='Email', null=True, blank=True, unique=True)
    name = models.CharField(db_column='Name', max_length=15, blank=True)
    role_id = models.IntegerField(db_column='Role_ID')
    markedfordeletion = models.BooleanField(db_column='MarkedForDeletion', default=False)
    firstname = models.CharField(db_column='FirstName', max_length=30, blank=True)
    lastname = models.CharField(db_column='LastName', max_length=30, blank=True)
    nickname = models.CharField(db_column='NickName', max_length=30, blank=True)
    gender = models.CharField(db_column='Gender', max_length=6, blank=True)
    department_id = models.CharField(db_column='DepartmentID', max_length=20, blank=True)
    status = models.CharField(db_column='Status', max_length=40, blank=True)
    ###
    # _permissions_cache_key = 'permissions_cache'
    # _flights_cache_key = 'flights_cache'
    # _equipments_cache_key = 'equipments_cache'
    # _activities_cache_key = 'activities_cache'
    # _views_cache_key = 'views_cache'
    # _alerts_cache_key = "alerts_cache"

    __permissions_fetched = False

    def __str__(self):
        return "{}|{}".format(self.userid, self.name)

    @property
    def is_authenticated(self):
        return True



    class Meta:
        db_table = 'Users'


class Departments(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(db_column='name', max_length=100)
    code = models.CharField(db_column='code', max_length=100)


    def __int__(self):
        return self.id

    class Meta:
        db_table = 'Departments'
