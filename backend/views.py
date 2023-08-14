from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.db.models import Sum, F
from ujson import loads as load_json

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact
from backend.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer, ProductSerializer
from info import SALT

class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'username','first_name', 'last_name', 'email', 'password', 'company', 'age', 'position'}.issubset(request.data):
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data['password']+SALT)
                user.save()                
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': user_serializer.errors})
        else:    
            return JsonResponse({'Status': False, 'Errors': 'Not all agruments'})
        
class LogInUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password']+SALT)
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True, 'Token': token.key})
                else:
                    return JsonResponse({'Status': False, 'Errors': 'Disable account'})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Wrong login or password'})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Not all arguments'})

class DetailAccount(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        else:           
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)    
        else:
            if 'password' in request.data:
                request.user.set_password(request.data['password'])
            user_serializer = UserSerializer(request.user, data=request.data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': user_serializer.errors})        

class CategoryView(APIView):
    def get(self, request, *args, **kwargs):
        category = Category.objects.all()           
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if Category.objects.get(name=request.data["name"]) is True:        
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
        else:
            return JsonResponse({"Status": False, "Errors": "Already exist"})     
    

class ShopView(APIView):
    def get(self, request, *args, **kwargs):
        shop = Shop.objects.all()           
        serializer = CategorySerializer(shop, many=True)
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated and request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not Allowed'}, status=403) 
        request.data.update({'user_id': request.user.id})     
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': serializer.errors})
            
class ContactView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        else:
            contact = Contact.objects.filter(user_id=request.user.id)
            serializer = ContactSerializer(contact, many=True)
            return Response(serializer.data)
        
    def post(self,request,*args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        elif {'city', 'street', 'phone'}.issubset(request.data):
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Authentification mistake or Incorrect arguments'})
        
    def delete(self,request, *args,**kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        elif {'id'}.issubset(request.data):
            try:
                Contact.objects.filter(id=request.data['id'], user_id=request.user.id).delete()
                return JsonResponse({'Status': 'Done'})           
            except:
                return JsonResponse({'Status': False, 'Errors': 'Incorrect arguments'})
            
    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        else:
            contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
            serializer = ContactSerializer(contact, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

class ProductInfoView(APIView):
    def get(self,request, *args, **kwargs):
        product = ProductInfo.objects.filter(product=request.data['product_id'], shop=request.data['shop_id'])
        product_serializer = ProductInfoSerializer(product, many = True)
        return Response(product_serializer.data)
    
    def post(self,request,*args,**kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)        
        elif {'product_info', 'quantity'}.issubset(request.data):            
            serializer = ProductInfoSerializer(data=request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
        else: 
            return JsonResponse({"Status": False, "Errors": 'Not all arguments'})

    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        shop = Shop.objects.filter(id=request.data['shop_id'])
        shop_serializer = ShopSerializer(shop, many = True)
        if shop_serializer.data[0]['user_id'] != request.user.id:
            return JsonResponse({'Status': False, 'Error': 'Wrond user'})
        product_info = ProductInfo.objects.filter(id=request.data['product_info_id']).first()
        product_info_serializer = ProductInfoSerializer(product_info, data=request.data, partial=True)
        if product_info_serializer.is_valid():
            product_info_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': product_info_serializer.errors})
        
    def delete(self,request, *args,**kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        shop = Shop.objects.filter(id=request.data['shop_id'])
        shop_serializer = ShopSerializer(shop, many = True)
        if shop_serializer.data[0]['user_id'] != request.user.id:
            return JsonResponse({'Status': False, 'Error': 'Wrond user'})
        elif {'id'}.issubset(request.data):
            try:
                ProductInfo.objects.filter(id=request.data['id']).delete()
                return JsonResponse({'Status': 'Done'})           
            except:
                return JsonResponse({'Status': False, 'Errors': 'Incorrect arguments'})
            
class BasketView(APIView):
    def get(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)
    
    def post(self,request,*args,**kwargs):
        if not request.user.is_authenticated or request.user.type != 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        elif {'product_info_id', 'quantity'}.issubset(request.data):
            contact = Contact.objects.filter(user_id=request.user.id)
            serializer_contact = ContactSerializer(contact, many=True)
            order = {'user': request.user.id,'contact': serializer_contact.data[0]['id'], 'status': 'basket'}
            order_serializer = OrderSerializer(data=order)
            if order_serializer.is_valid():
                creation_order = order_serializer.save()
                order_items = {'quantity': request.data['quantity'], 
                               'product_info_id': request.data['product_info_id'], 
                                'order': creation_order.id
                            }
                # print(request.data['product_info_id'])
                order_items_serializer = OrderItemSerializer(data=order_items)
                if order_items_serializer.is_valid():
                    order_items_serializer.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': 'Not work'})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Not working'})
                
    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type != 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order_item = OrderItem.objects.filter(id=request.data['id']).first()
        print(order_item.__dict__)
        order_item_serializer = OrderItemSerializer(order_item, data=request.data, partial = True)
        if order_item_serializer.is_valid():
            order_item_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False})

    def delete(self,request, *args,**kwargs):
        if not request.user.is_authenticated or request.user.type != 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        shop = Order.objects.filter(id=request.data['id']).delete()
        return JsonResponse({'Status': 'Done'})
           