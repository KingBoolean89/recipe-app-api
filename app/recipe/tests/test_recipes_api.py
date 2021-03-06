from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def sample_tag(user, name='Main Course'):
        return Tag.objects.create(user=user, name=name) 

def sample_ingredient(user, name='Cinnanmon'):
        return Ingredient.objects.create(user=user, name=name) 

def detail_url(recipe_id):
    
    return reverse('recipe:recipe-detail', args=[recipe_id])
           

def sample_recipe(user, **params):
    defaults = {
        'title':'Sample Recipe',
        'time_minutes':10,
        'price':5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):

     def setUp(self):
         self.client = APIClient()

     def test_login_required(self):

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test2@gmail.com',
            'testpass',
            )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        sample_recipe(user=self.user)  
        sample_recipe(user=self.user)  
        
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipes_limited_to_user(self):

        user2 = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass',
            )
        
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def tets_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user)) 

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_basic_recipe(self):
        payload = {
            'title':'Sample Recipe',
            'time_minutes':10,
            'price':5.00,
        }  
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe,key))  

    def test_create_recipe_with_tags(self):

        tag1 = sample_tag(user=self.user, name='Tag1')
        tag2 = sample_tag(user=self.user, name='Tag2') 
        payload = {
            'title':'Sample Recipe 2',
            'time_minutes':30,
            'price':15.00,
            'tags':[tag1.id, tag2.id]
        } 
        res = self.client.post(RECIPES_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])  
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user,name='Ingredient1')
        ingredient2 = sample_ingredient(user=self.user,name='Ingredient2') 

        payload = {
            'title':'Sample Recipe 2',
            'time_minutes':30,
            'price':25.00,
            'ingredients':[ingredient1.id, ingredient2.id]
        } 
        res = self.client.post(RECIPES_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])  
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)


    def test_partial_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title':'Spaghetti',
            'time_minutes':25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)





              
     
    
     


