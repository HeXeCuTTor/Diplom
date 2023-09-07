import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse
from model_bakery import baker
import json

from backend.models import User, Shop, Category, Product, Contact

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def make_user():
    def users(*args,**kwargs):
        baker.make(User,*args, **kwargs)
        id_user = User.objects.filter(username='Test_User').first().id
        return Token.objects.create(user_id=id_user)
    
    return users

@pytest.fixture
def make_category():
    def categories(*args, **kwargs):
        return baker.make(Category, *args, **kwargs)
    
    return categories

@pytest.fixture
def make_shops():
    def shops(*args, **kwargs):
        return baker.make(Shop, *args, **kwargs)
    
    return shops

@pytest.fixture
def make_contacts():
    def contacts(*args, **kwargs):
        return baker.make(Contact, *args, **kwargs)
    
    return contacts

@pytest.mark.django_db
def test_get_categories(client):
    response = client.get('/api/v1/categories')
    assert response.status_code == 200

@pytest.mark.django_db
def test_post_category(client, make_user):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    response = client.post('/api/v1/categories', json.dumps({
                                                    "name": "tank"
                                                  }), content_type="application/json", 
                                                  **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            )
    assert response.status_code == 200
    assert 'tank' == Category.objects.values()[0]['name']

@pytest.mark.django_db
def test_post_shops(client, make_user):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    response = client.post('/api/v1/shops', json.dumps({
                                                        "name": "shopp",
                                                        "url": "http://iuitm.com"
                                                        }), content_type="application/json", 
                                                        **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            )
    assert response.status_code == 200
    assert 'shopp' == Shop.objects.values()[0]['name']

@pytest.mark.django_db
def test_patch_user_account(client, make_user):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    response = client.post('/api/v1/user/detail_account', 
                            json.dumps({
                                          "username": "NEW_USER",
                                          "email":"oooio0@gmail.com",
                                          "age":"55",
                                          "password": "gfrdcr6668"
                                        }), content_type="application/json", 
                                        **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            )
    assert response.status_code == 200
    assert 'NEW_USER' == User.objects.values()[0]['username']

@pytest.mark.django_db
def test_get_user_data(client, make_user):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    response = client.post('/api/v1/user/detail_account',
                            content_type="application/json", 
                            **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            )
    assert response.json() == {'Status': True} 
    assert User.objects.values()[0]['username'] == 'Test_User' 

@pytest.mark.django_db
def test_post_products(client, make_user, make_category):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    make_category(name="Category_1")
    id_category = Category.objects.filter(name='Category_1').first().id
    response = client.post('/api/v1/products', 
                            json.dumps({
                                          "category_id": id_category,
                                          "name": "Acer"
                                        }), content_type="application/json", 
                                        **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            )
    assert response.json() == {'Status': True}
    assert Product.objects.values()[0]['name'] == "Acer"
    
@pytest.mark.django_db
def test_get_products(client):
    response = client.get('/api/v1/products')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_shops(client):
    response = client.get('/api/v1/shops')
    assert response.status_code == 200

@pytest.mark.django_db
def test_post_shops(client, make_user, make_shops):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    user_id = User.objects.filter(username='Test_User').first().id
    make_shops(user_id=user_id)
    shops_id = Shop.objects.filter(user_id=user_id).first().id
    response = client.patch('/api/v1/shops',
                            json.dumps({
                                          "id": shops_id,
                                          "name": "гггuulнн sho77p",
                                          "url": "http://check.ru",
                                        }), content_type="application/json", 
                                        **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            ) 
    assert response.status_code == 200
    assert Shop.objects.values()[0]['name'] == "гггuulнн sho77p"

@pytest.mark.django_db
def test_get_contacts(client, make_user):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    response = client.get('/api/v1/user/contacts', content_type="application/json", 
                                                **{"HTTP_AUTHORIZATION":'Token ' + token.key})
    assert response.status_code == 200

@pytest.mark.django_db
def test_post_contacts(client, make_user):
    token = make_user(username = "Test_User", age = 77, type = 'shop')
    response = client.post('/api/v1/user/contacts',
                           json.dumps({
                                        "city": "uoooooo",
                                        "house": "hhgerg",
                                        "street": "qweqwed",
                                        "structure": "12123",
                                        "building": "2424",
                                        "apartment": "46623",
                                        "phone":"+34234234"
                                        }), content_type="application/json",
                                        **{"HTTP_AUTHORIZATION":'Token ' + token.key}
                            )
    assert response.status_code == 200
    assert Contact.objects.values()[0]['city'] == "uoooooo"



                                        



