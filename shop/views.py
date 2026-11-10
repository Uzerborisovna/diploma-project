from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Product, Category, Shop, Contact, Order, OrderItem
from .serializers import (
    ProductSerializer, CategorySerializer, ShopSerializer,
    RegisterSerializer, UserSerializer, ContactSerializer,
    OrderSerializer
)
from django.core.mail import send_mail

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = [AllowAny]


class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response({'error': 'contact_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        
        order = Order.objects.create(user=request.user, contact=contact)
        
        cart_items = request.data.get('items', [])
        items_text = ""
        for item in cart_items:
            product = get_object_or_404(Product, id=item['product_id'])
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                shop=product.shop,
                quantity=item['quantity'],
                price=product.price
            )
            items_text += f"{product.name} (x{item['quantity']}) - {product.price} руб.\n"
        
        # Письмо клиенту
        send_mail(
            subject=f'Подтверждение заказа №{order.id}',
            message=f'Спасибо за заказ! Ваш заказ №{order.id} принят.',
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        
        # Письмо администратору (накладная)
        send_mail(
            subject=f'Накладная по заказу №{order.id}',
            message=f'Поступил новый заказ №{order.id} от {request.user.username}.\n\nТовары:\n{items_text}',
            from_email=None,
            recipient_list=['admin@diploma-project.local'],
            fail_silently=False,
        )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
