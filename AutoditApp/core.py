from django.db import connections
from collections import defaultdict, OrderedDict



@staticmethod
def dict_fetch_all(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        OrderedDict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@staticmethod
def fetch_data(query):
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        data = dict_fetch_all(cursor)
        return data