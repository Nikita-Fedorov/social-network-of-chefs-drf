from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers import UserSerializer, SubscriptionUserSerializer

from .models import User, Follow


class SubscribeListViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionUserSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_to_sub = get_object_or_404(User, pk=pk)
        user = request.user

        if user != user_to_sub:
            if not Follow.objects.filter(
                user=user, author=user_to_sub
            ).exists():
                Follow.objects.create(user=user, author=user_to_sub)
                user_to_modify_serializer = UserSerializer(
                    user_to_sub, context={'request': request}
                )
                return Response(user_to_modify_serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            else:
                return Response({'error': 'Пользователь уже подписан'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
        else:
            return Response({'error': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

    def delete(self, request, pk):
        user_to_sub = get_object_or_404(User, pk=pk)
        user = request.user

        if Follow.objects.filter(user=user, author=user_to_sub).exists():
            Follow.objects.filter(user=user, author=user_to_sub).delete()
            user_to_modify_serializer = UserSerializer(
                user_to_sub,
                context={'request': request}
            )
            return Response(user_to_modify_serializer.data,
                            status=status.HTTP_204_NO_CONTENT
                            )
        else:
            return Response(
                {'Ошибка отписки: пользователь не был подписан'},
                status=status.HTTP_400_BAD_REQUEST
                )
