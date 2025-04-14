from django.urls import path

from app.user.views import UserDetail, UserLogin, UserLogout, UserRegister


urlpatterns = [
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', UserLogout.as_view(), name='user-logout'),

    path('', UserRegister.as_view(), name='user-register'),
    path('detail/', UserDetail.as_view(), name='user-detail'),
]