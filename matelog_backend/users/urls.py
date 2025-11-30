from django.urls import path
from .views import (UserRegistrationView, UserLoginView, UserLogoutView,
                    UserProfileView, RegistrationChoicesView)
from .csrf_views import get_csrf_token

app_name = 'users'

urlpatterns = [
    path('csrf/', get_csrf_token, name='csrf'),
    path('choices/', RegistrationChoicesView.as_view(), name='choices'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]