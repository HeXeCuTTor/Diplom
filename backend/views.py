from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.contrib.auth import authenticate

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact
from backend.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer
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

class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.filter(status='active')
    serializer_class = ShopSerializer

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

        