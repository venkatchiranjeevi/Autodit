from django.conf.urls import url
from AutoditApp.Admin_Handler import views

urlpatterns = [
    url("^control-details", views.AdminControlHandlerAPI.as_view()),
    url("^framework-details", views.AdminFrameworkHandlerAPI.as_view()),
    url("^all-policies", views.AdminPolicyHandlerAPI.as_view()),
    url("^control-map-details", views.AdminControlsBlockDetails.as_view()),
    url("^policy-create", views.AdminPolicyCreateHandler.as_view()),
    url("^policy-template-parameters", views.PolicyVariablesHandler.as_view()),
    url("^policy-control-handler", views.PolicyFrameworkControlHandler.as_view()),
    url("^get-policy-details", views.AdminSinglePolicyHandler.as_view()),


]