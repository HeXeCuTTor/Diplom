from django.urls import path

from backend.views import RegisterUser,LogInUser, DetailAccount, CategoryView, ShopView, ContactView, ProductInfoView, \
    OrdersView, ProductView, RepairAccountView, ProductUploadFile,ConfirmAccountUser

app_name = 'backend'
urlpatterns = [
    path('categories', CategoryView.as_view(), name='categories'),
    path('products', ProductView.as_view(), name='products'),
    path('shops', ShopView.as_view(), name='shops'),
    path('user/recovery_password', RepairAccountView.as_view(), name='recovery_password'),
    path('user/register', RegisterUser.as_view(), name='register'),
    path('user/register/confirm', ConfirmAccountUser.as_view(), name='confirm'),
    path('user/login', LogInUser.as_view(), name='login'),
    path('user/detail_account',DetailAccount.as_view(), name='detail_account'),
    path('user/contacts', ContactView.as_view(), name='contacts'),
    path('product/info', ProductInfoView.as_view(), name='product_info'),
    path('product/upload_file', ProductUploadFile.as_view(), name='upload_file'),
    path('orders', OrdersView.as_view(), name='orders')
]