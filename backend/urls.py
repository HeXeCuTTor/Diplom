from django.urls import path

from backend.views import RegisterUser,LogInUser, DetailAccount, CategoryView, ShopView, ContactView, ProductInfoView, \
    BasketView

app_name = 'backend'
urlpatterns = [
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('user/register', RegisterUser.as_view(), name='register'),
    path('user/login', LogInUser.as_view(), name='login'),
    path('user/detail_account',DetailAccount.as_view(), name='detail_account'),
    path('user/contacts', ContactView.as_view(), name='contacts'),
    path('product/info', ProductInfoView.as_view(), name='product_info'),
    path('basket/info', BasketView.as_view(), name='basket_user')
]