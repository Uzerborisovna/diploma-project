from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import uuid
from .models import (
    Product, ProductInfo, Category, Shop, Contact,
    Order, OrderItem, ConfirmEmailToken
)
from .serializers import (
    ProductInfoSerializer, CategorySerializer, ShopSerializer,
    RegisterSerializer, UserSerializer, ContactSerializer,
    OrderSerializer, LoginSerializer, ConfirmEmailSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            token = serializer.validated_data['token']
            try:
                user = User.objects.get(email=email)
                confirm_token = ConfirmEmailToken.objects.get(user=user, token=token)
                user.is_active = True
                user.save()
                confirm_token.delete()
                return Response({'Status': True})
            except (User.DoesNotExist, ConfirmEmailToken.DoesNotExist):
                return Response({'Status': False, 'Errors': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_active:
                    return Response({'Status': False, 'Errors': 'Email not confirmed'},
                                    status=status.HTTP_401_UNAUTHORIZED)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'Status': True, 'token': token.key})
            return Response({'Status': False, 'Errors': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductInfoListView(generics.ListAPIView):
    queryset = ProductInfo.objects.filter(quantity__gt=0, shop__state=True)
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]


class ProductInfoDetailView(generics.RetrieveAPIView):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
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
        return Response({'Status': True, 'Contacts': serializer.data})

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'Status': True, 'Contact': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'Status': False, 'Errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        contact.delete()
        return Response({'Status': True})


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order, _ = Order.objects.get_or_create(user=request.user, state='basket')
        serializer = OrderSerializer(order)
        return Response({'Status': True, 'Cart': serializer.data})

    def post(self, request):
        order, _ = Order.objects.get_or_create(user=request.user, state='basket')
        product_info_id = request.data.get('product_info_id')
        quantity = int(request.data.get('quantity', 1))

        product_info = get_object_or_404(ProductInfo, id=product_info_id)

        if product_info.quantity < quantity:
            return Response({'Status': False, 'Errors': 'Not enough quantity'}, status=status.HTTP_400_BAD_REQUEST)
        if not product_info.shop.state:
            return Response({'Status': False, 'Errors': 'Shop is not accepting orders'},
                            status=status.HTTP_400_BAD_REQUEST)

        order_item, created = OrderItem.objects.get_or_create(
            order=order, product_info=product_info, defaults={'quantity': quantity}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()

        return Response({'Status': True})

    def delete(self, request, item_id):
        order, _ = Order.objects.get_or_create(user=request.user, state='basket')
        item = get_object_or_404(OrderItem, id=item_id, order=order)
        item.delete()
        return Response({'Status': True})


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(state='basket')


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
            return Response({'Status': False, 'Errors': 'contact_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        contact = get_object_or_404(Contact, id=contact_id, user=request.user)

        order, _ = Order.objects.get_or_create(user=request.user, state='basket')
        order_items = order.items.all()

        if not order_items:
            return Response({'Status': False, 'Errors': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        items_text = "\n".join(
            [f"{item.product_info.product.name} (x{item.quantity}) - {item.product_info.price} руб." for item in
             order_items])

        for item in order_items:
            if item.product_info.quantity < item.quantity:
                return Response({'Status': False, 'Errors': f'Not enough {item.product_info.product.name}'},
                                status=status.HTTP_400_BAD_REQUEST)
            item.product_info.quantity -= item.quantity
            item.product_info.save()

        order.contact = contact
        order.state = 'new'
        order.save()

        try:
            send_mail(
                subject=f'Подтверждение заказа №{order.id}',
                message=f'Спасибо за заказ! Ваш заказ №{order.id} принят.',
                from_email=None,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
            send_mail(
                subject=f'Накладная по заказу №{order.id}',
                message=f'Поступил новый заказ №{order.id} от {request.user.username}.\n\nТовары:\n{items_text}',
                from_email=None,
                recipient_list=['admin@diploma-project.local'],
                fail_silently=True,
            )
        except Exception:
            pass

        serializer = OrderSerializer(order)
        return Response({'Status': True, 'Order': serializer.data}, status=status.HTTP_201_CREATED)


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        if not request.user.is_staff and order.user != request.user:
            return Response({'Status': False, 'Errors': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        new_state = request.data.get('state')
        if new_state:
            order.state = new_state
            order.save()
            return Response({'Status': True})
        return Response({'Status': False, 'Errors': 'state is required'}, status=status.HTTP_400_BAD_REQUEST)