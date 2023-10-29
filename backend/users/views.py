from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Follow, User
from users.serializers import (UserSerializer, SubscriptionUserSerializer)


class UserView(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscriptionUserSerializer(
                self.paginate_queryset(
                    User.objects.filter(following__user=request.user)
                ),
                many=True,
                context={'request': request},
            ).data
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        follow, created = Follow.objects.get_or_create(
            user=request.user,
            author_id=id
        )
        if created:
            return Response(
                {'detail': 'Вы подписались на пользователя'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'detail': 'Вы уже подписаны на пользователя'},
            status=status.HTTP_200_OK
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        follow = get_object_or_404(Follow, user=request.user, author=id)
        follow.delete()
        return Response(
            {'detail': 'Вы отписались от пользователя'},
            status=status.HTTP_204_NO_CONTENT
        )
