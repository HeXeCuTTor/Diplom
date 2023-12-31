from rest_framework import serializers
from backend.models import User, Shop, Category, Parameter, Product, ProductInfo, ProductParameter, Contact, Order, OrderItem


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'status', 'url', 'user')
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'company', 'age')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category',)
        read_only_fields = ('id',)


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('name',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer
    product_parameters = ProductParameterSerializer(read_only=True, many=True)


    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'info_id', 'product', 'product_parameters', 'shop', 'quantity', 'price', 'price_rrc',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer


    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True)
    contact = ContactSerializer

    total_sum = serializers.IntegerField()


    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'status', 'creation_time', 'contact', 'total_sum', 'user',)
        read_only_fields = ('id',)          


