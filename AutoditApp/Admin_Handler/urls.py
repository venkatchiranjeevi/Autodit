from django.conf.urls import url
from AutoditApp.Admin_Handler import views
urlpatterns = [
    url("^controls", views.AdminControlHandlerAPI.as_view()),
    url("^frameworks", views.AdminFrameworkHandlerAPI.as_view()),
]