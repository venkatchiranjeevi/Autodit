from django.conf.urls import url
from AutoditApp import user_management
from AutoditApp.user_management import UserProfile
from AutoditApp.views import DepartmentsAPI, RolesAPI, SettingManagementAPI, ControlsManagementAPI, GlobalVariablesAPI, \
    PolicyManagementAPI, TenantGlobalVariablesAPI, TenantFrameworkMasterAPI, TenantLogoUploaderAPI, PolicyDetailsAPI, \
    ControlsManagementAPIALl, TenantPolicyDetails, PolicyDetailsHandler, PolicyContentHandler

urlpatterns = [
    url("user/", user_management.UsersList.as_view()),
    url("^users/profile/", UserProfile.as_view()),
    url("^departments/", DepartmentsAPI.as_view()),
    url("^roles/", RolesAPI.as_view()),

    url("^settings/", SettingManagementAPI.as_view()),
    url("^control-management/", ControlsManagementAPI.as_view()),
    url("^policy-management/", PolicyManagementAPI.as_view()),
    # url("^get-tenant-policies/", TenantPolicyDetails.as_view()),
    url("^global/variables", GlobalVariablesAPI.as_view()),
    url("^tenant/global/variables", TenantGlobalVariablesAPI.as_view()),
    url("^tenant/frameworks", TenantFrameworkMasterAPI.as_view()),
    # url("^tenant/all", ControlsManagementAPIALl.as_view()),

    url("^tenant/logo", TenantLogoUploaderAPI.as_view()),
    url("^policy/get-details", PolicyDetailsAPI.as_view()),
    url("^policy/policy-details", PolicyDetailsHandler.as_view()),
    url("^policy/update-content", PolicyContentHandler.as_view())

]