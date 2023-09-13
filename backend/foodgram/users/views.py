from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import SubscribeSerializer

from .models import Subscribe, User
from .serializers import CustomUserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        follower = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            follower,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=request.user, author=follower)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id=None):
        follower = get_object_or_404(User, id=id)
        Subscribe.objects.filter(user=self.request.user,
                                 author=follower).delete()
        return Response({'message': 'Вы отписаны'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(author__user=request.user))
        serializer = SubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
