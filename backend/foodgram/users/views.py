from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.serializers import SubscribeSerializer

from .models import Subscribe
from .serializers import RegisterUserSerializer, UserSerilizer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для пользователей"""
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerilizer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterUserSerializer
        return UserSerilizer

    def get_object(self):
        user = self.request.user
        pk = self.kwargs['pk']

        if pk == 'me' and user.is_authenticated:
            return user

        return get_object_or_404(User, pk=pk)

    def subscribed(self, serializer, id=None):
        follower = get_object_or_404(User, id=id)
        if self.request.user == follower:
            return Response({'message': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow = Subscribe.objects.get_or_create(user=self.request.user,
                                                 author=follower)
        serializer = SubscribeSerializer(follow[0])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, serializer, id=None):
        follower = get_object_or_404(User, id=id)
        Subscribe.objects.filter(user=self.request.user,
                                 author=follower).delete()
        return Response({'message': 'Вы отписаны'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, serializer, pk=None):
        if self.request.method == 'DELETE':
            return self.unsubscribed(serializer, pk)
        return self.subscribed(serializer, pk)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, serializer):
        following = Subscribe.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(following)
        serializer = SubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
