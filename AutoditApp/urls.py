from django.conf.urls import url
from AutoditApp import user_management
from AutoditApp.user_management import UserProfile
from AutoditApp.views import Departments

urlpatterns = [
    url("user/", user_management.UsersList.as_view()),
    url("^users/profile/", UserProfile.as_view()),
    url("^departments/", Departments.as_view()),
    url("^roles/", Departments.as_view()),


]