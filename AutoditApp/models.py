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


class TenantControlMaster(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    tenant_id = models.IntegerField(db_column='tenantId', blank=True)
    tenant_framework_id = models.IntegerField(db_column='TenantFrameworkId')
    master_control_id = models.IntegerField(db_column="Master_Control_Id", blank=True)
    control_type = models.CharField(db_column='type', max_length=50, blank=True)
    control_name = models.CharField(db_column="ControlName", max_length=500, blank=True)
    control_description = models.TextField(db_column='Description', null=True)
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)
    created_by = models.CharField(db_column="created_by", blank=True, max_length=150)
    master_framework_id = models.IntegerField(db_column="masterFrameworkId")


    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantControlMaster'


class TenantControlAudit(Base):
    id = models.AutoField(primary_key=True, db_column='Id')
    tenant_id = models.IntegerField(db_column='tenantId', blank=True)
    tenant_framework_id = models.IntegerField(db_column='TenantFrameworkId')
    control_code = models.CharField(db_column="ControlCode", null=True, max_length=100)
    old_control_name = models.CharField(db_column='OldControlName', max_length=50, blank=True)
    new_control_name = models.CharField(db_column="newControlName", max_length=500, blank=True)
    old_control_description = models.TextField(db_column='OldDescription', null=True)
    new_control_description = models.TextField(db_column='newDescription', null=True)
    version = models.CharField(db_column="version", null=True, max_length=100)
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)
    created_by = models.CharField(db_column="created_by", blank=True, max_length=150)
    tenant_control_id = models.IntegerField(db_column="TenantControlId", null=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantControlAudit'



class TenantHierarchyMapping(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id = models.IntegerField(db_column='tenantId')
    # TODO can we delete need to check
    master_hierarchy_id = models.IntegerField(db_column='masterHierarchyId')
    category = models.CharField(db_column='Category', max_length=150)
    tenant_policy_id = models.IntegerField(db_column='TenantPolicyId')
    is_deleted = models.IntegerField(db_column='is_delete', default=0)
    is_active = models.IntegerField(db_column='is_active', default=1)
    tenant_framework_id = models.IntegerField(db_column='tenantFrameworkId')
    tenant_control_id = models.IntegerField(db_column='tenantControlId')

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
    control_type = models.CharField(db_column='type', max_length=120)
    framework_id = models.IntegerField(db_column='FrameworkId', blank=False)
    control_code = models.CharField(db_column="ControlCode", null=True, max_length=100)
    description = models.TextField(db_column='Description', null=True, blank=True)
    category = models.CharField(db_column='Category', max_length=150,  null=True)
    is_deleted = models.IntegerField(db_column='IsDeleted', default=0)
    is_active = models.IntegerField(db_column='IsActive', default=1)
    created_by = models.CharField(db_column="created_by", null=True, max_length=150)


    def __int__(self):
        return self.id

    class Meta:
        db_table = 'ControlMaster'


class HirerecyMapper(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    f_id = models.IntegerField(db_column='Fid', null=True, blank=True)
    p_id = models.IntegerField(db_column='Pid', null=True, blank=True)
    c_id = models.IntegerField(db_column='Cid', null=True, blank=True)
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
    policy_code= models.CharField(db_column="policy_code", max_length=120)
    category = models.CharField(db_column='Category', max_length=120)
    policy_reference = models.CharField(db_column='policyReference', max_length=500)
    created_by = models.CharField(db_column='created_by', max_length=120)
    version = models.IntegerField(db_column='version', default=1)
    user_id = models.CharField(db_column='UserId', max_length=150)
    policy_file_name = models.CharField(db_column='policyFileName', max_length=250)
    policy_summery = models.TextField(db_column='Summery', blank=True)
    tennant_id = models.IntegerField(db_column='tennant_id', blank=False)
    def __int__(self):
        return self.id

    class Meta:
        db_table = 'PolicyMaster'



class TenantPolicyManager(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id = models.IntegerField(db_column='tenant_id', null=False)
    tenant_policy_name = models.CharField(db_column='tenantPolicyName', max_length=120)
    category = models.CharField(db_column='Category', max_length=120)
    policy_reference = models.CharField(db_column='policyReference', max_length=500)
    summery = models.TextField(db_column='summery', null=True)
    created_by = models.CharField(db_column='created_by', max_length=120)
    version = models.IntegerField(db_column='version', default=1)
    editor = models.IntegerField(db_column='editor', null=True)
    reviewer = models.IntegerField(db_column='reviewer', null=True)
    approver = models.IntegerField(db_column='approver', null=True)
    status = models.IntegerField(db_column='Status', default=1)
    departments = models.TextField(db_column='Departments', null=True)
    is_active = models.IntegerField(db_column='IsActive', default=1)
    state = models.CharField(db_column='State', max_length=50, default='Editing')
    user_id = models.CharField(db_column='UserId', max_length=150, default='')
    parent_policy_id = models.IntegerField(db_column='ParentPolicyID', null=True)
    review_period = models.CharField(db_column='reviewPeriod', null=True, max_length=20)
    published_date = CustomDateTimeField(db_column='publishedDate', null=True)
    code = models.CharField(db_column='code', max_length=50)
    policy_file_name=models.CharField(db_column='policyFileName', max_length=250, null=True)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantPolicyManager'


class MasterPolicyParameter(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    policy_id = models.IntegerField(db_column='policyId')
    type= models.CharField(db_column="type", max_length=50)
    parameter_key = models.CharField(db_column='parameterKey', max_length=250)
    parameter_type = models.CharField(db_column='parameterType', max_length=250)
    parameter_value = models.CharField(db_column='parameterValue', max_length=500)
    description = models.TextField(db_column='Description')
    created_by = models.CharField(db_column='createdBy', max_length=150)
    is_deleted = models.IntegerField(db_column='is_deleted', default=0)
    is_active = models.IntegerField(db_column='is_active', default=1)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'MasterPolicyParameter'


class TenantPolicyVersionHistory(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id = models.IntegerField(db_column='tenantId')
    policy_id = models.IntegerField(db_column='policyId')
    tenant_policy_name = models.CharField(db_column='tenantPolicyName', max_length=250)
    old_version = models.CharField(db_column='oldVersion', max_length=10)
    new_version = models.CharField(db_column='newVersion', max_length=10)
    policy_file_name = models.CharField(db_column='policyFileName', max_length=250)

    class Meta:
        db_table = 'TenantPolicyVersionHistory'


class TenantPolicyParameter(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id=models.IntegerField(db_column='tenantId')
    policy_id = models.IntegerField(db_column='policyId')
    type= models.CharField(db_column="type", max_length=50)
    parameter_key = models.CharField(db_column='parameterKey', max_length=250)
    parameter_type = models.CharField(db_column='parameterType', max_length=250)
    parameter_value = models.CharField(db_column='parameterValue', max_length=500)
    description = models.TextField(db_column='Description')
    created_by = models.CharField(db_column='createdBy', max_length=150)
    is_deleted = models.IntegerField(db_column='is_deleted', default=0)
    is_active = models.IntegerField(db_column='is_active', default=1)


    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantPolicyParameter'


class TenantPolicyDepartments(Base):
    id = models.AutoField(primary_key=True, db_column='id')
    tenant_id = models.IntegerField(db_column='tenant_id')
    tenant_policy_id = models.IntegerField(db_column='TenantPolicyID')
    tenant_dep_id = models.IntegerField(db_column="TenantDepartment_id")
    created_by = models.CharField(db_column='createdBy', max_length=150)
    is_active = models.IntegerField(db_column="IsActive", default=True)
    created_by = models.CharField(db_column='created_by', max_length=150)

    def __int__(self):
        return self.id

    class Meta:
        db_table = 'TenantPolicyDepartments'


# ADMIN AUDIT
# CUSTOM TAGS
# CKEDITOR API'S
# POLICY STATES
