"""Serializers for recipe API"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient, IngredientQuantity
from django.contrib.auth import get_user_model

class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients"""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientQuantitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')

    class Meta:
        model = IngredientQuantity
        fields = ['id', 'name', 'quantity']

class RecipeSerializer(serializers.ModelSerializer):
    
    tags = TagSerializer(many=True, required=False)
    
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']
    
    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(**validated_data)
        if tags is not None:
            self._get_or_create_tags(tags, recipe)
        
        return recipe
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
        
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""
    ingredients = IngredientQuantitySerializer(
        source='ingredientquantity_set',
        many=True,
        read_only=True
    )
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'ingredients']