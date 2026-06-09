from rest_framework import serializers
from purchases.models import Purchase, Order, Comment, Category
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'rating')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon')


class PurchaseListSerializer(serializers.ModelSerializer):
    organizer = UserShortSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    status_label = serializers.CharField(read_only=True)
    participants_count = serializers.IntegerField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    price_with_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Purchase
        fields = (
            'id', 'title', 'organizer', 'category', 'status', 'status_label',
            'price_per_unit', 'price_with_fee', 'organizer_fee',
            'stop_date', 'delivery_date', 'participants_count',
            'is_open', 'created_at',
        )


class PurchaseDetailSerializer(PurchaseListSerializer):
    class Meta(PurchaseListSerializer.Meta):
        fields = PurchaseListSerializer.Meta.fields + (
            'description', 'delivery_address', 'source_url',
            'min_participants', 'max_participants', 'total_units',
        )


class OrderSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    status_label = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'purchase', 'user', 'quantity', 'comment', 'status', 'status_label', 'total_price', 'created_at')
        read_only_fields = ('user', 'status')


class CommentSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'created_at')
        read_only_fields = ('author',)
