from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='testtaguser@example.com', password='testtaguser'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTest(TestCase):
    "Tests unauthentication API requests"
    
    def setUp(self):
        self.client = APIClient()
    
    def test_tags_unauthorized(self):
        """Test auth is required for retriving tags"""
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateTagsApiTest(TestCase):
    """Test authentication API requests"""
    
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_tags_retrive_success(self):
        
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Non-Veg')
        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_tags_limited_to_user(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Non-Veg')
        
        other_user = create_user('othertestuser@example.com', 'othertestuser')
        
        Tag.objects.create(user=other_user, name='Protien')
        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {'name': 'dessert'}
        
        url = detail_url(tag_id=tag.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        
    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        url = detail_url(tag_id=tag.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)