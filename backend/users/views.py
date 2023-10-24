from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from users.serializers import (UserSerializer, SubscriptionUserSerializer,
                               FollowSerializer)


class SubscribeListViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionUserSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = FollowSerializer(
            data={'user': request.user.id, 'author': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(follower=request.user, author_id=pk)
        return Response(UserSerializer(
            get_object_or_404(User, pk=pk),
            context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user_to_sub = get_object_or_404(User, pk=pk)
        user = request.user

        user_follows = user_to_sub.follower.filter(author=user)

        if user_follows.exists():
            user_follows.delete()
            user_to_modify_serializer = UserSerializer(
                user_to_sub,
                context={'request': request}
            )
            return Response(
                user_to_modify_serializer.data,
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'Ошибка отписки: пользователь не был подписан'},
            status=status.HTTP_400_BAD_REQUEST
        )
