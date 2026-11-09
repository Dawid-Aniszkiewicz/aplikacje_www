from rest_framework import serializers
from .models import Event, Category
from django.contrib.auth.models import User


class EventSerializer(serializers.Serializer):
    """
    Niskopoziomowy serializator modelu Event dziedziczący po serializers.Serializer.
    Wszystkie pola oraz operacje zapisu definiujemy jawnie.
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    slug = serializers.SlugField(required=True, max_length=220)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=False
    )
    organizer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='organizer'
    )
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    location = serializers.CharField(max_length=255)
    date = serializers.DateTimeField()
    capacity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_published = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)

    # Implementacja operacji utrwalania danych (saving instances):
    # Zob. https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        """
        Tworzy i zwraca nową instancję modelu Event na podstawie zwalidowanych danych.
        """
        return Event.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Aktualizuje istniejącą instancję modelu Event i zwraca ją.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.category = validated_data.get('category', instance.category)
        instance.organizer = validated_data.get('organizer', instance.organizer)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.date = validated_data.get('date', instance.date)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.price = validated_data.get('price', instance.price)
        instance.is_published = validated_data.get('is_published', instance.is_published)
        instance.save()
        return instance