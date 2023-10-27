from django.urls import include, path, re_path
from rest_framework import routers
from users.views import SubscribeView, SubscribeListViewSet

router = routers.DefaultRouter()

router.register(
    'users/subscriptions',
    SubscribeListViewSet,
    basename='subscriptions'
)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('users/<int:pk>/subscribe/',
         SubscribeView.as_view(), name='subscribe'
         ),
]
