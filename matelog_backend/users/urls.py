from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    RegistrationChoicesView,
    CSRFTokenView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('choices/', RegistrationChoicesView.as_view(), name='choices'),
    path('csrf/', CSRFTokenView.as_view(), name='csrf'),
]