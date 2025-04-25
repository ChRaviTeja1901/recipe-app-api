"""
Tests for recipe APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient, IngredientQuantity
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os
from PIL import Image

RECIPES_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

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
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_create_recipe_with_new_tag(self):
        payload = {
            'title': 'Thai Prawn Cury',
            'time_minutes': '25',
            'price': Decimal('50.99'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'], user=self.user
            ).exists()
            self.assertTrue(exists)
        
    def test_create_recipe_with_existing_tag(self):
        tag_thai = Tag.objects.create(user=self.user, name='Thai')
        payload = {
            'title': 'Thai Prawn Cury',
            'time_minutes': '25',
            'price': Decimal('50.99'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_thai, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'], user=self.user
            ).exists()
            self.assertTrue(exists)
    
    def test_create_tag_on_update(self):
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]}
        
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag_indian = Tag.objects.get(user=self.user, name='Indian')
        self.assertIn(tag_indian, recipe.tags.all())
    
    def test_update_tag_on_updating_recipe(self):
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_indian)
        
        tag_thai = Tag.objects.create(user=self.user, name='Thai')
        payload = {'tags': [{'name': 'Thai'}]}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag_indian, recipe.tags.all())
        self.assertIn(tag_thai, recipe.tags.all())
        
    def test_clear_tag(self):
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_indian)
        
        payload = {'tags': []}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag_indian, recipe.tags.all())
    
    def test_create_and_update_recipe_with_ingredients(self):
        # Create Recipe
        payload_create = {
            "title": "Fruit Salad",
            "time_minutes": 5,
            "price": 10.00,
            "ingredients": [
                {"name": "Apple"},
                {"name": "Banana"},
            ]
        }

        res = self.client.post(RECIPES_URL, payload_create, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe_id = res.data['id']

        # Update Recipe: change Banana to Mango
        url = detail_url(recipe_id=recipe_id)
        payload_update = {
            "ingredients": [
                {"name": "Apple"},
                {"name": "Mango"}
            ]
        }

        res = self.client.patch(url, payload_update, format='json')
        self.assertEqual(res.status_code, 200)
        recipe = Recipe.objects.get(id=recipe_id)
        self.assertEqual(recipe.ingredients.count(), 3)
        
        
    def test_create_and_update_recipe_with_ingredients(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Mango')
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)
        recipe.ingredients.add(ingredient)
        payload_update = {"ingredients": []}

        res = self.client.patch(url, payload_update, format='json')
        self.assertEqual(res.status_code, 200)
        recipe = Recipe.objects.get(id=recipe.id)
        self.assertEqual(recipe.ingredients.count(), 0)

class ImageUploadTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'usertest@gmail.com',
            'testtestuser'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)
        
    def tearDown(self):
        self.recipe.image.delete()
        
    
    def test_upload_image(self):
        url = image_upload_url(recipe_id=self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))