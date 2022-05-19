from django.conf.urls import url
from AutoditApp.auth import views

urlpatterns = [

    url("^login/", views.PasswordLogin.as_view()),
    url("^password/change/", views.PasswordChange.as_view())

    ]