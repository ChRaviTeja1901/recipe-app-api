from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from core.models import Recipe, Tag, Ingredient
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from recipe.serializers import IngredientSerializer, RecipeDetailSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='testuser1@gmail.com', password='testtestuser'):
    return get_user_model().objects.create_user(email=email, password=password)

def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

class PublicIngredientsApiTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def test_unauthorized_retrive(self):
        
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateIngredientsApiTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        
        self.client.force_authenticate(self.user)
    
    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name='Flour')
        Ingredient.objects.create(user=self.user, name='Sugar')
        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_retrieve_ingredients(self):
        user2 = create_user(email='user2@example.com', password='testtestuser')
        Ingredient.objects.create(user=user2, name='Flour')
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
    
    def test_update_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Flour')
        
        payload = {'name': 'sugar'}
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
        
    def test_delete_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Flour')
        Ingredient.objects.create(user=self.user, name='Sugar')
        Ingredient.objects.create(user=self.user, name='Salt')
        
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.delete(url)
        
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(ingredient.name, serializer.data)
    
    def test_delete_ingredient(self):
        ingredient1 = Ingredient.objects.create(user=self.user, name='Flour')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Rice Flour')
        recipe = Recipe.objects.create(
            title='Roti',
            time_minutes=10,
            price=Decimal('5.99'),
            user = self.user
        )
        recipe.ingredients.add(ingredient1)
        
        res = self.client.get(INGREDIENTS_URL, {'assinged_only': 1})
        
        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)