from django.urls import path

from backend.views import RegisterUser,LogInUser, DetailAccount, CategoryView, ShopView, ContactView, ProductInfoView, \
    OrdersView, ProductView, RepairAccountView

app_name = 'backend'
urlpatterns = [
    path('categories', CategoryView.as_view(), name='categories'),
    path('products', ProductView.as_view(), name='products'),
    path('shops', ShopView.as_view(), name='shops'),
    path('user/recovery_password', RepairAccountView.as_view(), name='recovery_account'),
    path('user/register', RegisterUser.as_view(), name='register'),
    path('user/login', LogInUser.as_view(), name='login'),
    path('user/detail_account',DetailAccount.as_view(), name='detail_account'),
    path('user/contacts', ContactView.as_view(), name='contacts'),
    path('product/info', ProductInfoView.as_view(), name='product_info'),
    path('orders', OrdersView.as_view(), name='orders')
]