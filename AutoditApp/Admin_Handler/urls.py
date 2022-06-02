from django.conf.urls import url
from AutoditApp.Admin_Handler import views
urlpatterns = [
    url("^controls", views.AdminControlHandlerAPI.as_view()),
    url("^frameworks", views.AdminFrameworkHandlerAPI.as_view()),
    url("^policies", views.AdminPolicyHandlerAPI.as_view()),
    url("^control-map-details", views.AdminControlsBlockDetails.as_view()),
    url("^policy-create", views.AdminPolicyCreateHandler.as_view()),

]