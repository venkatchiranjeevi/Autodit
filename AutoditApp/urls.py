from django.conf.urls import url
from AutoditApp import user_management
from AutoditApp.user_management import UserProfile
from AutoditApp.views import DepartmentsAPI, RolesAPI, SettingManagementAPI, ControlsManagementAPI, GlobalVariablesAPI, \
    PolicyManagementAPI, TenantGlobalVariablesAPI, TenantFrameworkMasterAPI, TenantLogoUploaderAPI, PolicyDetailsAPI, \
    ControlsManagementAPIALl, ControlManagementDetailAPI, ControlManagementDetailHistoryAPI, \
    PolicyDetailsHandler, PolicyContentHandler, MetaDetailsHandler, PolicyDepartmentsHandler, TenantPolicyCustomTags, \
    TenantPolicyVariables, PolicyCommentsHandler, PolicyEligibleUsers, PolicyStatesHandler, PolicyVersionHistory, \
    PolicyVersionHistoryDetails, TenantPolicyLifeCycleUsersAPI, SubscriptionsPolicyAPI, PolicyRenewUpdateAPI, \
    DashBoardAPIHandler, SubscriptionPaymentHandlerAPI

urlpatterns = [
    url("user/", user_management.UsersList.as_view()),
    url("^users/profile/", UserProfile.as_view()),
    url("^departments/", DepartmentsAPI.as_view()),
    url("^roles/", RolesAPI.as_view()),
    url("^meta-details", MetaDetailsHandler.as_view()),
    url("^settings/", SettingManagementAPI.as_view()),
    url("^control-management/", ControlsManagementAPI.as_view()),
    url("^control-details/", ControlManagementDetailAPI.as_view()),
    url("^control-history/", ControlManagementDetailHistoryAPI.as_view()),
    url("^policy-management/", PolicyManagementAPI.as_view()),
    # url("^get-tenant-policies/", TenantPolicyDetails.as_view()),
    url("^global/variables", GlobalVariablesAPI.as_view()),
    url("^tenant/global/variables", TenantGlobalVariablesAPI.as_view()),
    url("^tenant/policy-parameters", TenantPolicyVariables.as_view()),

    url("^tenant/frameworks", TenantFrameworkMasterAPI.as_view()),
    url("^tenant/logo", TenantLogoUploaderAPI.as_view()),
    url("^policy/get-policy", PolicyDetailsAPI.as_view()),
    url("^policy/policy-renew-update", PolicyRenewUpdateAPI.as_view()),
    url("^policy/policy-details", PolicyDetailsHandler.as_view()),
    url("^policy/update-content", PolicyContentHandler.as_view()),
    url("^policy/department", PolicyDepartmentsHandler.as_view()),
    url("^policy/custom-tags", TenantPolicyCustomTags.as_view()),
    url("^policy/eligible-users", PolicyEligibleUsers.as_view()),
    url("^policy/comments", PolicyCommentsHandler.as_view()),
    url("^policy/state-change", PolicyStatesHandler.as_view()),
    url("^policy/version_history", PolicyVersionHistory.as_view()),
    url("^policy/version-history-details", PolicyVersionHistoryDetails.as_view()),
    url("^policy/lifecycle-users", TenantPolicyLifeCycleUsersAPI.as_view()),
    url("user-dashboard", DashBoardAPIHandler.as_view()),
    url("^subscriptions/create", SubscriptionsPolicyAPI.as_view()),
    url("^subscriptions/payment/handle", SubscriptionPaymentHandlerAPI.as_view())
]