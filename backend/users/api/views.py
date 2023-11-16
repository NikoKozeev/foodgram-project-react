from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.api.pagination import UserPagination
from users.api.permissions import AuthorOrReadOnly
from users.api.serializers import (UserSerializer,
                                   PostSubscribeSerializer,
                                   SubscribeUserSerializer)
from users.models import Subscription, User


class UserViewSet(UserViewSet):
    """User view Set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = (AuthorOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated(), ]
        if self.action == 'create':
            return [AllowAny(), ]
        return [AuthorOrReadOnly(), ]

    @action(methods=['get'],
            permission_classes=(IsAuthenticated,),
            detail=False,)
    def subscriptions(self, request):
        """All user subscriptions."""
        page = self.paginate_queryset(User.objects.filter(
            author__subscriber=request.user))
        serializer = SubscribeUserSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def subscribe(self, request, id):
        """Subscribe to an author."""
        subscriber = request.user
        data = {'subscriber': subscriber.id, 'author': id}
        serializer = PostSubscribeSerializer(data=data,
                                             context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id):
        """Unsubscribe from an author."""
        data = Subscription.objects.filter(subscriber_id=request.user.id,
                                           author_id=id)
        if data.exists():
            data.delete()
            return Response({'You have unsubscribed from the author'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'Invalid data'},
                        status=status.HTTP_400_BAD_REQUEST)
