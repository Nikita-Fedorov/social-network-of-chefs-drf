from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Follow, User
from users.serializers import (CustomUserSerializer,
                               SubscriptionUserSerializer,
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
        serializer.save()
        return Response(CustomUserSerializer(
            get_object_or_404(User, pk=pk),
            context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user_to_sub = get_object_or_404(User, pk=pk)
        user = request.user
        follow_exists = Follow.objects.filter(
            user=user, author=user_to_sub
        ).exists()

        if follow_exists:
            Follow.objects.filter(user=user, author=user_to_sub).delete()
            user_serializer = CustomUserSerializer(
                user_to_sub,
                context={'request': request}
            )
            return Response(
                user_serializer.data,
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'Ошибка отписки: пользователь не был подписан'},
                status=status.HTTP_400_BAD_REQUEST
            )
