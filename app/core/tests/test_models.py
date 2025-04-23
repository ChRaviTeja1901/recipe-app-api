"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

def create_user(user='testuser@example.com', password='testtestuser'):
    return get_user_model().objects.create_user(user=user, password=password)

class ModelTests(TestCase):
    """Tests Model"""
    
    def test_create_user_with_email_successful(self):
        email = 'testuser@gmail.com'
        password = 'testtestuser'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@example.COM', 'test1@example.com'],
            ['Test2@EXAMPLE.COM', 'Test2@example.com'],
            ['test3@Example.com', 'test3@example.com'],
            ['TEST4@Example.com', 'TEST4@example.com']
        ]
        
        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='testtestuser'
            )
            
            self.assertEqual(user.email, expected_email)
    
    def test_create_user_without_email_raises_valueerror(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testtestuser')
            
    def test_create_super_user(self):
        user = get_user_model().objects.create_superuser('test@example.com', 'testtestuser')
        
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_create_recipe(self):
        user = get_user_model().objects.create_user('test@example.com', 'testtestuser')
        
        recipe = models.Recipe.objects.create(
            user = user,
            title = 'Sample Recipe Name',
            time_minutes = 5,
            price = Decimal('5.50'),
            description = 'Sample Recipe Description'
        )
        
        self.assertEqual(str(recipe), recipe.title)
    
    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, tag='tag1')
        
        self.assertEqual(str(tag), tag.name)