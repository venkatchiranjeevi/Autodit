from django.conf.urls import url
from AutoditApp import user_management


urlpatterns = [

    url("r^add_user/", user_management.UsersList.as_view())


]