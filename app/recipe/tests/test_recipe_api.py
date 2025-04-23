"""
Tests for recipe APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    default = {
        'title' : 'Sample Recipe Name',
        'time_minutes' : 5,
        'price' : Decimal('5.50'),
        'description' : 'Sample Recipe Description',
        'link': 'https://example.com/recipe.pdf'
    }
    
    default.update(params)
    return Recipe.objects.create(user=user, **default)

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

class PublicRecipeAPITests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Tests auth required for accessing recipes"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateRecipeAPITests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testuser@example.com',
            'testtestuser'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_list_limited_to_user(self):
        
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'testttestother'
        )
        
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
    
    def test_retrieve_recipe(self):
        recipe = create_recipe(user=self.user)
        
        url = detail_url(recipe_id=recipe.id)
        
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)
        
        # print("Response Data:", res.data)
        # print(serializer.data)
        self.assertEqual(res.data, serializer.data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
    
    def test_create_recipe(self):
        """Test Create Recipe"""
        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 10,
            'price': Decimal('5.99')
        }
        
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
    def test_partial_update(self):
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe One'
        )
        
        payload = {'title': 'Sample Recipe Two'}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.link, original_link)
        
    
    def test_update_user_returns_error(self):
        new_user = get_user_model().objects.create_user(email='test2user@gmail.com', password='test2testuser')
        recipe = create_recipe(user=self.user)
        
        payload = {'user': new_user.id}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url,payload)
        
        recipe.refresh_from_db()
        self.assertEqual(res.user, self.user)