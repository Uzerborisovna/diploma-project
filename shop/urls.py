from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('shops/', views.ShopListView.as_view(), name='shops'),
    path('contacts/', views.ContactView.as_view(), name='contacts'),
    path('contacts/<int:contact_id>/', views.ContactView.as_view(), name='contact-detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/<int:item_id>/', views.CartView.as_view(), name='cart-item'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
]
