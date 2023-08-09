from django.urls import path

from backend.views import CategoryView, ShopView

app_name = 'backend'
urlpatterns = [
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),

]