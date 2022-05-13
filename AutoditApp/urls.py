from django.conf.urls import url
from AutoditApp import user_management

urlpatterns = [

    url("users/", user_management.UsersList.as_view())

    ]