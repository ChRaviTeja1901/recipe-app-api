"""
Tests for user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Tests for create and return user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the public features of User API"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_create_user_success(self):
        """Test for creating user"""
        payload = {
            'email': 'test1@example.com',
            'password': 'testtestuser',
            'name': 'Test One'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        
    def test_create_user_with_email_exists_error(self):
        payload = {
            'email': 'test1@example.com',
            'password': 'testtestuser',
            'name': 'Test One'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_too_short_error(self):
        payload = {
            'email': 'test1@example.com',
            'password': 'test',
            'name': 'Test One'
        }
        res= self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            'email': 'test1@example.com',
            'password': 'testtestuser',
            'name': 'Test One'
        }
        
        create_user(**user_details)
        
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_create_token_bad_credentials(self):
        """Test not generate token for bad credentials"""
        user_details = {
            'email': 'test1@example.com',
            'password': 'testtestuser',
            'name': 'Test One'
        }
        
        create_user(**user_details)
        
        payload = {
            'email': user_details['email'],
            'password': user_details['password'] + 'more'
        }
        
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_profile_unauthorized(self):
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""
    
    def setUp(self):
        user_details = {
            'email': 'test1@example.com',
            'password': 'testtestuser',
            'name': 'Test One'
        }
        
        self.user = create_user(**user_details)
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_success(self):
        """Test retriving the profile for authenticated user"""
        
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })
    
    def test_post_me_not_allowed(self):
        """Test post me not allowed"""
        
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_user_profile(self):
        
        payload = {'name': 'test update one', 'password': 'testtestupdateuser'}
        
        res = self.client.patch(ME_URL, payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)