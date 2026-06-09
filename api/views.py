from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from purchases.models import Purchase, Order, Comment, Category
from .serializers import (
    PurchaseListSerializer, PurchaseDetailSerializer,
    OrderSerializer, CommentSerializer, CategorySerializer
)


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        organizer = getattr(obj, 'organizer', None) or getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return organizer == request.user or request.user.is_staff


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class PurchaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price_per_unit', 'stop_date']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Purchase.objects.filter(is_active=True).select_related('organizer', 'category')
        category = self.request.query_params.get('category')
        status_filter = self.request.query_params.get('status')
        if category:
            qs = qs.filter(category__slug=category)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PurchaseDetailSerializer
        return PurchaseListSerializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        purchase = self.get_object()
        if purchase.organizer != request.user and not request.user.is_staff:
            return Response({'detail': 'Нет доступа.'}, status=status.HTTP_403_FORBIDDEN)
        orders = purchase.orders.select_related('user').all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        purchase = self.get_object()
        comments = purchase.comments.select_related('author').all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('purchase')

    def perform_create(self, serializer):
        purchase_id = self.request.data.get('purchase')
        purchase = Purchase.objects.get(pk=purchase_id)
        if not purchase.is_open:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Сбор заявок на эту закупку уже завершён.')
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ('pending', 'confirmed'):
            order.status = Order.STATUS_CANCELLED
            order.save()
            return Response({'status': 'cancelled'})
        return Response({'detail': 'Нельзя отменить в текущем статусе.'}, status=status.HTTP_400_BAD_REQUEST)
