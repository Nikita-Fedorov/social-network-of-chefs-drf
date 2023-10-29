from django.urls import include, path, re_path
from rest_framework import routers
from users.views import UserView


router = routers.DefaultRouter()

router.register('users', UserView, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    re_path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
