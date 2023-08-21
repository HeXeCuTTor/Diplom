from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.db.models import Sum, F
from yaml import load as load_yaml, Loader
from requests import get

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ResetEmailToken
from backend.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer, ProductSerializer
from info import SALT
from backend.signals import password_reset, new_order

class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'username','first_name', 'last_name', 'email', 'password', 'company', 'age', 'position'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data['password']+SALT)
                user.save()            
                #отправка email c ResetEmailToken 
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': user_serializer.errors})
        else:    
            return JsonResponse({'Status': False, 'Errors': 'Not all agruments'})
        

class ConfirmAccountUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            user = User.objects.filter(email=request.data['email']).first()
            token = ResetEmailToken.objects.filter(user_id=user.__dict__['id'],key=request.data['token']).first()
            # print(token)
            if token is not None:
                auth_token, _ = Token.objects.get_or_create(user=user)
                token.delete()
                return JsonResponse({'Status': True, 'Token': auth_token.key})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Wrong data'})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Not all arguments'})
        
class LogInUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password']+SALT)
            user_confirm = ResetEmailToken.objects.filter(user_id=user.id).first()
            if user is not None and user_confirm is None and user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({'Status': True, 'Token': token.key})
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

class RepairAccountView(APIView):
    def get(self, request, *args, **kwargs):
        if {'email'}.issubset(request.data):
            user = User.objects.filter(email = request.data['email']).first()
            password_reset.send(sender=self.__class__, user_id=user.__dict__['id'])
            return JsonResponse({'Status': "На ваш email отправлен токен для восстановления вашего аккаунта"}) 
        
    def post(self,request, *args, **kwargs):
        if {'token'}.issubset(request.data):
            user_id = ResetEmailToken.objects.filter(key = request.data['token']).first()
            user = User.objects.filter(id = user_id.__dict__['user_id']).first()
            user_serializer = UserSerializer(user, data=request.data, partial=True)
            if user_serializer.is_valid():
                created_user = user_serializer.save() 
                created_user.set_password(request.data['password']+SALT)
                user.save()
                ResetEmailToken.objects.get(user_id=user_id).delete()                              
            return JsonResponse({'Status': True}) 

class CategoryView(APIView):
    def get(self, request, *args, **kwargs):
        category = Category.objects.all()           
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        Category.objects.get_or_create(name=request.data["name"])       
        return JsonResponse({'Status': True})
  

class ShopView(APIView):
    def get(self, request, *args, **kwargs):
        shop = Shop.objects.all()           
        serializer = ShopSerializer(shop, many=True)
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})  
        # print(request.data)
        request.data.update({'user': request.user.id})
        # print(request.data)
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': serializer.errors})
        
    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})  
        shop = Shop.objects.filter(id=request.data['id']).first()
        # print(shop.__dict__['user_id'])    
        serializer = ShopSerializer(shop, data=request.data, partial=True)
        if shop.__dict__['user_id'] != request.user.id:
            return JsonResponse({'Status': False, 'Error': 'Wrond user'})        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': serializer.errors})
            
class ContactView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        if {'id'}.issubset(request.data):
            contact_id = request.data['id']
            contact = Contact.objects.filter(id=contact_id)
        else:
            contact_id = request.user.id
            contact = Contact.objects.filter(user_id=contact_id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)
        
    def post(self,request,*args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
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
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        elif {'id'}.issubset(request.data):
            try:
                Contact.objects.filter(id=request.data['id'], user_id=request.user.id).delete()
                return JsonResponse({'Status': 'Done'})           
            except:
                return JsonResponse({'Status': False, 'Errors': 'Incorrect arguments or user'})
        else: 
            return JsonResponse({"Status": False, "Errors": 'Not all arguments'})
        
    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        else:
            contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
            serializer = ContactSerializer(contact, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
class ProductView(APIView):
    def get(self, request, *args, **kwargs):
        product = Product.objects.all()           
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        Product.objects.get_or_create(name=request.data["name"], category_id=request.data['category_id'])       
        return JsonResponse({'Status': True}) 

class ProductInfoView(APIView): 
    def get(self,request, *args, **kwargs):
        product = ProductInfo.objects.filter(product=request.data['product_id'], shop=request.data['shop_id'])
        product_serializer = ProductInfoSerializer(product, many = True)
        return Response(product_serializer.data)
    
    def post(self,request,*args,**kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})       
        elif {'product', 'shop'}.issubset(request.data):        
            serializer = ProductInfoSerializer(data=request.data, partial = True)
            if serializer.is_valid():
                creation_product_info = serializer.save()
                if {'product_parameters'}.issubset(request.data):
                    for name, value in request.data['product_parameters'][0].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=creation_product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)
                else:
                    return JsonResponse({'Status': True, 'Info': 'Another parameters is none'})                      
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
        else: 
            return JsonResponse({"Status": False, "Errors": 'Not all arguments'})

    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        shop = Shop.objects.filter(id=request.data['shop'])
        shop_serializer = ShopSerializer(shop, many = True)
        # print(shop_serializer.data[0]['user'])
        if shop_serializer.data[0]['user'] != request.user.id:
            return JsonResponse({'Status': False, 'Error': 'Wrond user'})
        product_info = ProductInfo.objects.filter(id=request.data['product_info_id']).first()
        # print(product_info)
        product_info_serializer = ProductInfoSerializer(product_info, data=request.data, partial=True)
        if product_info_serializer.is_valid():
            creation_product_info = product_info_serializer.save()
            if {'product_parameters'}.issubset(request.data):
                for name, value in request.data['product_parameters'][0].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.update_or_create(product_info_id=creation_product_info.id,
                                                                parameter_id=parameter_object.id,
                                                                defaults = {'value': value})
            else:
                return JsonResponse({'Status': True, 'Info': 'Another parameters is none'})              
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': product_info_serializer.errors})
        
    def delete(self,request, *args,**kwargs):
        if not request.user.is_authenticated or request.user.type == 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        shop = Shop.objects.filter(id=request.data['shop'])
        shop_serializer = ShopSerializer(shop, many = True)
        if shop_serializer.data == []:
            return JsonResponse({'Status': False, 'Error': 'Not found'})
        if shop_serializer.data[0]['user'] != request.user.id:
            return JsonResponse({'Status': False, 'Error': 'Wrond user'})
        elif {'id'}.issubset(request.data):
            try:
                ProductInfo.objects.filter(id=request.data['id']).delete()
                return JsonResponse({'Status': 'Done'})           
            except:
                return JsonResponse({'Status': False, 'Errors': 'Incorrect arguments'})
            
class OrdersView(APIView):
    def get(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        if request.user.type != 'buyer':
            basket = Order.objects.filter(
                user_id=request.user.id, status='basket').prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter').annotate(
                total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
            serializer = OrderSerializer(basket, many=True)
            return Response(serializer.data)
        else:
            order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data)           
    
    def post(self,request,*args,**kwargs):
        if not request.user.is_authenticated or request.user.type != 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        if {'product_info', 'quantity'}.issubset(request.data):
            order = {'user': request.user.id, 'status': 'basket'}
            order_serializer = OrderSerializer(data=order,partial=True)
            if order_serializer.is_valid():
                creation_order = order_serializer.save()
                order_items = {'quantity': request.data['quantity'], 
                               'product_info': request.data['product_info'], 
                                'order': creation_order.id
                            }
                # print(request.data['product_info_id'])
                order_items_serializer = OrderItemSerializer(data=order_items)
                if order_items_serializer.is_valid():
                    order_items_serializer.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': order_items_serializer.errors})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Not working'})
          
    def patch(self,request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        order = Order.objects.filter(id=request.data['id']).first()
        if request.user.type != 'shop' and 'contact' in request.data:
            order_update = {'status': 'new',
                            'contact': request.data['contact']
                        }
            order_serializer = OrderSerializer(order, data=order_update,partial=True)
            if order_serializer.is_valid():
                order_serializer.save()
                order_item = OrderItem.objects.filter(order_id=request.data['id']).first()
                order_item_serializer = OrderItemSerializer(order_item, data=request.data, partial = True)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()
                    new_order.send(sender=self.__class__, user_id=request.user.id)
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': order_item_serializer.errors})
            else:
                return JsonResponse({'Status': False, 'Errors': order_serializer.errors})
        elif request.user.type == 'shop':
            order.update(status= request.data['status'])
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Not all arguments'})

    def delete(self,request, *args,**kwargs):
        if not request.user.is_authenticated or request.user.type != 'buyer':
            return JsonResponse({'Status': False, 'Error': 'Not authorized user'})
        order = Order.objects.filter(id=request.data['id']).first()
        if order.__dict__['status'] != 'basket':
            return JsonResponse({'Status': False, 'Error': 'Order cancel impossible'})
        else:
            order.delete()
        return JsonResponse({'Status': 'Done'})

class ProductUploadFile(APIView):
    def post(self,request,*args,**kwargs):
        url = request.data.get('url')
        data = get(url).content
        json_data = load_yaml(data, Loader=Loader)
        shop, _ = Shop.objects.get_or_create(name=json_data['shop'], user_id=request.user.id)
        for category in json_data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        ProductInfo.objects.filter(shop_id=shop.id).delete() 
        for goods in json_data['goods']:
            product, _ = Product.objects.get_or_create(name=goods['name'], category_id=goods['category'])
            product_info = ProductInfo.objects.create(product=product,
                                                      info_id=goods['id'],
                                                      model=goods['model'],
                                                      price=goods['price'],
                                                      price_rrc=goods['price_rrc'],
                                                      quantity=goods['quantity'],
                                                      shop=shop)
            if {'parameters'}.issubset(goods):
                for name, value in goods['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.update_or_create(product_info_id=product_info.id,
                                                                parameter_id=parameter_object.id,
                                                                defaults = {'value': value})
        return JsonResponse({'Status': 'Done'})                   


#импорт шаблона yaml
#коррекция urls
#Celery???
           