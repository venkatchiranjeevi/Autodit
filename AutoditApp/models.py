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
    tenant_id = models.IntegerField(db_column='tenantId')
    department_id = models.IntegerField(db_column='DepartmentId',null=True)

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


class TenantDepartment(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(db_column='name', max_length=100)
    code = models.CharField(db_column='code', max_length=100)
    tenant_id = models.IntegerField(db_column='tenant_id', blank=True)
    is_active = models.IntegerField(db_column='is_active', blank=True, default=True)
    description = models.TextField(db_column="dep_description", blank=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantDepartment'


class TenantDocumentMaster(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id = models.IntegerField(db_column='tenant_id')
    t_document_name = models.CharField(db_column='tenantDocumentName', max_length=100)
    document_url = models.IntegerField(db_column='document_url', blank=True)
    version = models.IntegerField(db_column='version', blank=True, default=None)
    created_by = models.CharField(db_column='created_by', max_length=100)
    description = models.TextField(db_column="dep_description", blank=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantDocumentMaster'


class TenantGlobalVariables(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    key = models.CharField(db_column='key', max_length=120)
    key_type = models.CharField(db_column='key_type', max_length=120, blank=True)
    value = models.CharField(db_column='value', max_length=120, blank=True)
    result = models.CharField(db_column='result', max_length=120, blank=True, default=None)
    tenant_id = models.IntegerField(db_column='TenantId', null=True, blank=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantGlobalVariables'


class Tenant(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(db_column='name', max_length=100)
    tenant_details = models.CharField(db_column='tenant_details', max_length=100)
    properties = models.TextField(db_column='properties', null=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'Tenant'


class TenantFrameworkMaster(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_framework_name = models.CharField(db_column='TenantFrameworkName', max_length=50)
    master_framework_id = models.IntegerField(db_column='MasterFId')
    framework_type = models.CharField(db_column='type', max_length=50, blank=True)
    description = models.TextField(db_column='Description', default='')
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)
    tenant_id = models.IntegerField(db_column='tenantId', null=True, blank=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantFrameworkMaster'


class TenantHierarchyMapping(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    controller_id = models.IntegerField(db_column='controller_id', null=True, blank=True)
    controller_name = models.CharField(db_column='controller_name', max_length=120)
    principle_id = models.IntegerField(db_column='principle_id', null=True, blank=True)
    framework_id = models.IntegerField(db_column='framework_id', null=True, blank=True)
    department_id = models.IntegerField(db_column='department_id', null=True, blank=True)
    controller_description = models.TextField(db_column='controller_description', null=True, blank=True)
    created_by = models.CharField(db_column='created_by', max_length=120, null=True, blank=True)
    tenant_id = models.IntegerField(db_column='tenantId')
    master_hierarchy_id = models.IntegerField(db_column='masterHierarchyId')
    category = models.CharField(db_column='Category', max_length=150)
    tenant_policy_id = models.IntegerField(db_column='TenantPolicyId')
    is_deleted = models.IntegerField(db_column='is_delete', default=0)
    is_active = models.IntegerField(db_column='is_active', default=1)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantHierarchyMapping'


class GlobalVariables(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    key = models.CharField(db_column='key', max_length=120)
    key_type = models.CharField(db_column='key_type', max_length=120, blank=True)
    value = models.CharField(db_column='value', max_length=120, blank=True)
    result = models.CharField(db_column='result', max_length=120, blank=True, default=None)
    description = models.TextField(db_column='Description', null=True, blank=True)
    category = models.CharField(db_column='Category', max_length=100, blank=True)
    created_by = models.CharField(db_column='created_by', max_length=120, null=True, blank=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'GlobalVariables'


class FrameworkMaster(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    framework_name = models.CharField(db_column='FrameworkName', max_length=120)
    framework_type = models.CharField(db_column='type', max_length=120, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'FrameworkMaster'


class ControlMaster(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    control_name = models.CharField(db_column='ControlName', max_length=120)
    control_type = models.CharField(db_column='type', max_length=120, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'ControlMaster'


class HirerecyMapper(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    f_id = models.IntegerField(db_column='Fid', null=True, blank=True)
    c_id = models.IntegerField(db_column='Pid', null=True, blank=True)
    p_id = models.IntegerField(db_column='Cid', null=True, blank=True)
    policy_id = models.IntegerField(db_column='PolicyId')
    # policy_reference = models.CharField(db_column='PolicyReference', max_length=500)
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'HirerecyMapper'


class PolicyMaster(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    policy_name = models.CharField(db_column='PolicyName', max_length=120)
    category = models.CharField(db_column='Category', max_length=120)
    policy_reference = models.CharField(db_column='policyReference', max_length=500)
    created_by = models.CharField(db_column='created_by', max_length=120)
    version = models.IntegerField(db_column='version', default=1)
    user_id = models.CharField(db_column='UserId', max_length=150)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'PolicyMaster'


class TenantPolicyManager(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id = models.IntegerField(db_column='tenant_id', null=False)
    tenant_policy_name = models.CharField(db_column='tenantPolicyName', max_length=120)
    category = models.CharField(db_column='Category', max_length=120)
    # policy_reference = models.CharField(db_column='policyReference', max_length=500)
    created_by = models.CharField(db_column='created_by', max_length=120)
    version = models.IntegerField(db_column='version', default=1)
    editor = models.IntegerField(db_column='editor')
    reviewer = models.IntegerField(db_column='reviewer')
    approver = models.IntegerField(db_column='approver')
    status = models.IntegerField(db_column='Status')
    departments = models.TextField(db_column='Departments')
    is_active = models.IntegerField(db_column='IsActive')
    state = models.CharField(db_column='State', max_length=50)
    user_id = models.CharField(db_column='UserId', max_length=150)


    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantPolicyManager'


# ADMIN AUDIT
# CUSTOM TAGS
# CKEDITOR API'S
# POLICY STATES
