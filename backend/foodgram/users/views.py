from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import SubscribeSerializer

from .models import Subscribe, User
from .serializers import CustomUserSerializer


class UserViewSet(UserViewSet):
    """Viewset для пользователей"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def subscribed(self, serializer, id=None):
        """Подписывает пользователя на автора"""
        follower = get_object_or_404(User, id=id)
        follow = Subscribe.objects.get_or_create(
            user=self.request.user, author=follower)
        if follow:
            return Response(
                {'message': 'Вы подписались на пользователя.'},
                status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, serializer, id=None):
        """Добавляем подписку"""
        return self.subscribed(serializer, id)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id=None):
        """Удаляем подписку"""
        follower = get_object_or_404(User, id=id)
        Subscribe.objects.filter(user=self.request.user,
                                 author=follower).delete()
        return Response({'message': 'Вы отписаны'},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Показывает подписки"""
        pages = self.paginate_queryset(
            User.objects.filter(author__user=request.user))
        serializer = SubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
