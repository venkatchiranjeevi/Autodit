from django.db import connections
from collections import defaultdict, OrderedDict
from AutoditApp.Utils import coalesce
from AutoditApp.sql_queries import ROLE_POLICIES
from AutoditApp.models import TenantDepartment as Departments, Roles, TenantGlobalVariables, Tenant
from django.db.models import Q

class BaseConstant:
    def __init__(self):
        pass


def dict_fetch_all(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        OrderedDict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def fetch_data_from_sql_query(query):
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
    role_id = "','".join([str(i) for i in eval(role_id)])
    query = ROLE_POLICIES.format(role_id)
    policies = fetch_data_from_sql_query(query)
    return policies


def get_users_by_tenant_id(all_users, tenant_id):
    for each_user in all_users:
        user_record = dict()
        all_attributes = dict()
        user_record['markedfordeletion'] = False if each_user.get("Enabled") == True else True
        for each_user_attrib in each_user.get("Attributes"):
            all_attributes[each_user_attrib.get('Name')] = each_user_attrib.get('Value')
        if all_attributes.get('custom:tenant_id') == str(tenant_id):
            user_record['mobnmbr'] = all_attributes.get('phone_number')[3:] if all_attributes.get('phone_number') \
                else None
            user_record['email'] = all_attributes.get('email', all_attributes.get("custom:Email_Address"))
            name = all_attributes.get("custom:Name") if all_attributes.get("custom:Name") else \
                all_attributes.get("name")
            user_record['name'] = name
            role = all_attributes.get('custom:role')
            user_record['roles'] = [roles_data.get(int(role))] if role and roles_data.get(int(role)) else []
            entity = all_attributes.get('custom:Entity')
            user_record['entity'] = int(entity) if entity else entity
            operation_unit = all_attributes.get('custom:Operation_Unit')
            user_record['operation_unit'] = int(operation_unit) if operation_unit else operation_unit
            user_record['userid'] = all_attributes.get("sub")
    pass




