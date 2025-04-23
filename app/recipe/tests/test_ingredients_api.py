from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from core.models import Recipe, Tag, Ingredient, IngredientQuantity
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from recipe.serializers import IngredientSerializer, RecipeDetailSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='testuser1@gmail.com', password='testtestuser'):
    return get_user_model().objects.create_user(email=email, password=password)

def create_recipe(user, **params):
    default = {
        'title' : 'Sample Recipe Name',
        'time_minutes' : 5,
        'price' : Decimal('5.50'),
        'description' : 'Sample Recipe Description',
        'link': 'https://example.com/recipe.pdf',
    }
    
    default.update(params)
    
    recipe = Recipe.objects.create(user=user, **default)
    
    tag, _ = Tag.objects.get_or_create(user=user, name='Indian')
    recipe.tags.add(tag)
    
    return recipe

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

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
        self.recipe = create_recipe(user=self.user)
        
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
        
    
    def test_retrive_ingredients_with_recipe(self):
        ingredient1 = Ingredient.objects.create(user=self.user, name='Flour')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Sugar')
        IngredientQuantity.objects.create(recipe = self.recipe, ingredient = ingredient1, quantity = '1 tbsp')
        IngredientQuantity.objects.create(recipe = self.recipe, ingredient = ingredient2, quantity = '2 sp')
        
        url = detail_url(recipe_id=self.recipe.id)
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(self.recipe)
        
        self.assertEqual(res.data, serializer.data)