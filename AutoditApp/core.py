from django.db import connections
from collections import defaultdict, OrderedDict
from AutoditApp.Utils import coalesce
from AutoditApp.sql_queries import ROLE_POLICIES
from AutoditApp.models import TenantDepartment as Departments, Roles, TenantGlobalVariables
from django.db.models import Q


def dict_fetch_all(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        OrderedDict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def fetch_data(query):
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        data = dict_fetch_all(cursor)
        return data


def get_session_value(request):
    return coalesce(request.META.get('HTTP_AUTHORIZATIONCODE', None),
                    request.GET.get('session', None),
                    request.META.get('HTTP_SESSION', None)
                    )


def get_policies_by_role(role_id):
    query = ROLE_POLICIES.format(role_id)
    policies = fetch_data(query)
    return policies


def get_department_data():
    department_data = Departments.objects.all().values("id", "name", "code", "tenant_id")
    return department_data


def save_department_data(data):
    result = Departments.objects.create(name=data.get("name"), code=data.get("code"), tenant_id=data.get("tenant_id"))
    return result


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


def delete_department(dep_id):
    Departments.objects.filter(id=dep_id).delete()
    return True


def get_roles_data():
    roles_data = Roles.objects.all().values("role_id", "role_name", "code")
    return roles_data


def get_tenant_global_varialbles(query):
    t_global_var_data = TenantGlobalVariables.objects.objects.filter(query).values()
    return t_global_var_data


def save_tenant_global_varialble(data):
    tbv_obj = TenantGlobalVariables.objects.create(key=data.get("key"), value=data.get("value"), key_type=data.get("key_type"),
                                         result=data.get("result"), created_by=data.get("created_by"))
    return tbv_obj