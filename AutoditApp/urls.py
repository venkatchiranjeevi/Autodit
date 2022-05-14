from django.conf.urls import url
from AutoditApp import user_management
from AutoditApp.user_management import UserProfile

urlpatterns = [
    url("user/", user_management.UsersList.as_view()),
    url("^users/profile/", UserProfile.as_view())

]