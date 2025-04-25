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
    ingredients = IngredientSerializer(many=True, required=False)
    
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']
    
    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)
    
    def _create_or_update_ingredients(self, ingredients_data, recipe):
        auth_user = self.context['request'].user

        for item in ingredients_data:
            name = item['name']

            ingredient, _ = Ingredient.objects.get_or_create(
                name=name,
                user=auth_user
            )
            recipe.ingredients.add(ingredient)

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        recipe = Recipe.objects.create(**validated_data)
        if tags is not None:
            self._get_or_create_tags(tags, recipe)
        
        if ingredients is not None:
            self._create_or_update_ingredients(ingredients, recipe)
        
        return recipe
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        
        if ingredients is not None:
            instance.ingredients.clear()
            self._create_or_update_ingredients(ingredients, instance)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
        
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        
class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}