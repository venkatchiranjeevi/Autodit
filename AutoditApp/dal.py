from AutoditApp.models import TenantDepartment as Departments, Roles, TenantGlobalVariables, Tenant, GlobalVariables
from django.db.models import Q


class BaseConstant:
    def __init__(self):
        pass


class AccessPolicy(BaseConstant):
    @staticmethod
    def create_access_policy(role_id):
        pass

class RolesData(BaseConstant):

    @staticmethod
    def get_roles_data():
        roles_data = Roles.objects.all().values("role_id", "role_name", "code")
        return roles_data

    @staticmethod
    def get_role_details(roles_ids):
        query = Q()
        if roles_ids:
            query &= Q(role_id__in=roles_ids)
        roles_data = Roles.objects.filter(query).values("role_id", "role_name", "code")
        return roles_data


    @staticmethod
    def save_roles_info(data):
        roles_instances = []
        for each_role in data:
            role_obj = Roles(role_name=each_role.get("role_name"), code=each_role.get("role_code"),
                             tenant_id=each_role.get("role_code"))
            roles_instances.append(role_obj)
        Roles.objects.bulk_create(roles_instances)
        return True

    @staticmethod
    def save_single_role(data):
        role_obj = Roles(role_name=data.get("role_name"), code=data.get("role_code"), tenant_id=data.get("tenant_id"))
        role_obj.save()
        return role_obj


class TenantMasterData(BaseConstant):

    @staticmethod
    def get_tenant_details(tenant_id=None):
        query = Q()
        if tenant_id:
            query &= Q(id=tenant_id)
        return Tenant.objects.filter(query).values()

    @staticmethod
    def save_tenant_master_data(data):
        tenant_obj = Tenant.objects.create(name=data.get("tenant_name"), tenant_details=data.get("details"),
                              properties=data.get("properties"))
        return tenant_obj


class DeparmentsData(BaseConstant):

    @staticmethod
    def get_department_data():
        department_data = Departments.objects.all().values("id", "name", "code", "tenant_id")
        return department_data

    @staticmethod
    def save_department_data(data):
        result = Departments.objects.create(name=data.get("name"), code=data.get("code"),
                                            tenant_id=data.get("tenant_id"))

        return result

    @staticmethod
    def update_department_data(data):
        department_obj = Departments.objects.get(id=id)
        is_active = data.get("is_active")
        description = data.get("description")
        if is_active:
            department_obj.is_active = is_active
        if description:
            department_obj.description = description
        department_obj.name = data.get("name")
        department_obj.code = data.code("code")
        department_obj.tenant_id = data.get("tenant_id")
        department_obj.save()
        return True

    @staticmethod
    def delete_department(dep_id):
        Departments.objects.filter(id=dep_id).delete()
        return True


class GlobalVariablesData(BaseConstant):
    @staticmethod
    def get_global_variables():
        global_variables = list(GlobalVariables.objects.all().values())
        return global_variables


class TenantGlobalVariableData(BaseConstant):

    @staticmethod
    def get_tenant_global_varialbles(query):
        t_global_var_data = TenantGlobalVariables.objects.filter(query).values()
        return t_global_var_data

    @staticmethod
    def save_tenant_global_varialble(data):
        tbv_obj = TenantGlobalVariables.objects.create(key=data.get("key"), value=data.get("value"),
                                                       key_type=data.get("key_type"),
                                                       result=data.get("result"), created_by=data.get("username"),
                                                       tenant_id=data.get("tenant_id"))
        return tbv_obj