from django.db import connections
from collections import defaultdict, OrderedDict
from AutoditApp.Utils import coalesce
from AutoditApp.sql_queries import ROLE_POLICIES
from AutoditApp.models import Departments


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
    department_data = Departments.objects.all().values("id", "name", "code")
    return department_data
