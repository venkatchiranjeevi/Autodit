from django.conf.urls import url
from AutoditApp import user_management
from AutoditApp.user_management import UserProfile
from AutoditApp.views import DepartmentsAPI, RolesAPI, SettingManagementAPI, ControlsManagementAPI,GlobalVariablesAPI,\
    PolicyManagementAPI

urlpatterns = [
    url("user/", user_management.UsersList.as_view()),
    url("^users/profile/", UserProfile.as_view()),
    url("^departments/", DepartmentsAPI.as_view()),
    url("^roles/", RolesAPI.as_view()),

    url("^settings/", SettingManagementAPI.as_view()),
    url("^control-management/", ControlsManagementAPI.as_view()),
    url("^policy-management/", PolicyManagementAPI.as_view()),
    url("^global/variables", GlobalVariablesAPI.as_view()),

]