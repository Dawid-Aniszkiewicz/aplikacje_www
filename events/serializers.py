from rest_framework import serializers
from django.utils import timezone
from .models import Category, Tag, Event
from django.contrib.auth.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    events_count = serializers.IntegerField(source='events.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'events_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'events_count']


class EventModelSerializer(serializers.ModelSerializer):
    # 1. Pola pomocnicze tylko do odczytu (zamiast samych kluczy obcych ID)
    category_name = serializers.ReadOnlyField(source='category.name')
    organizer_username = serializers.ReadOnlyField(source='organizer.username')

    # 2. Obsługa relacji ManyToMany (Tagi):
    # - w odpowiedziach GET zwracamy pełne obiekty tagów (id, name, slug)
    tags_details = TagSerializer(source='tags', many=True, read_only=True)
    # - w żądaniach POST/PUT/PATCH przyjmujemy tablicę identyfikatorów, np. "tag_ids": [1, 2]
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )

    # 3. Pola dynamiczne wyliczane metodą (SerializerMethodField)
    is_free = serializers.SerializerMethodField()
    days_until_event = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'organizer', 'organizer_username', 'tags_details', 'tag_ids',
            'description', 'location', 'date', 'capacity', 'price',
            'is_free', 'days_until_event', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_free(self, obj) -> bool:
        """Zwraca True, jeśli wydarzenie jest bezpłatne."""
        return obj.price == 0

    def get_days_until_event(self, obj) -> int:
        """Oblicza liczbę pełnych dni pozostałych do rozpoczęcia wydarzenia (lub 0, jeśli już minęło)."""
        delta = obj.date - timezone.now()
        return max(0, delta.days)

    # Walidacja na poziomie pojedynczego pola: data wydarzenia
    def validate_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Termin wydarzenia musi być datą w przyszłości!")
        return value

    # Walidacja na poziomie pojedynczego pola: minimalna pojemność sali
    def validate_capacity(self, value):
        if value < 5:
            raise serializers.ValidationError("Minimalna liczba uczestników wydarzenia wynosi 5 osób.")
        return value

    # Walidacja krzyżowa na poziomie całego obiektu (obsługuje również częściowy PATCH!)
    def validate(self, attrs):
        # Pobieramy wartości ze słownika attrs, a przy metodzie PATCH posiłkujemy się istniejącą instancją
        title = attrs.get('title', getattr(self.instance, 'title', ''))
        price = attrs.get('price', getattr(self.instance, 'price', 0))
        is_published = attrs.get('is_published', getattr(self.instance, 'is_published', True))
        description = attrs.get('description', getattr(self.instance, 'description', ''))
        location = attrs.get('location', getattr(self.instance, 'location', ''))
        capacity = attrs.get('capacity', getattr(self.instance, 'capacity', 0))

        # Reguła biznesowa 1: słowo "darmowy"/"bezpłatny"/"free" w tytule wymusza cenę 0.00 PLN
        if any(word in title.lower() for word in ['darmow', 'bezpłatn', 'free']) and price > 0:
            raise serializers.ValidationError({
                "price": "Wydarzenie oznaczone w tytule jako bezpłatne nie może mieć ceny wyższej niż 0.00 PLN."
            })

        # Reguła biznesowa 2: publikowane wydarzenie musi mieć opis o długości min. 20 znaków
        if is_published and len(description.strip()) < 20:
            raise serializers.ValidationError({
                "description": "Opublikowane wydarzenie musi posiadać szczegółowy opis (minimum 20 znaków)."
            })

        # Reguła biznesowa 3: wydarzenie online ("online"/"webinar" w tytule lub opisie) musi mieć URL w lokalizacji
        is_url = location.startswith('http://') or location.startswith('https://')
        if any(word in title.lower() or word in description.lower() for word in ['online', 'webinar']) and not is_url:
            raise serializers.ValidationError({
                "location": "Dla wydarzeń online pole lokalizacji musi zawierać poprawny adres URL (http:// lub https://)."
            })

        # Reguła biznesowa 4: wydarzenie stacjonarne może mieć maksymalnie 1000 miejsc
        if not is_url and capacity > 1000:
            raise serializers.ValidationError({
                "capacity": "Wydarzenie stacjonarne nie może mieć więcej niż 1000 miejsc."
            })

        return attrs


class EventListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    organizer_username = serializers.ReadOnlyField(source='organizer.username')
    is_free = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'category_name', 'organizer_username',
            'date', 'location', 'price', 'is_free', 'short_description', 'tags_count'
        ]

    def get_is_free(self, obj) -> bool:
        """Zwraca True, jeśli wydarzenie jest bezpłatne."""
        return obj.price == 0

    def get_short_description(self, obj) -> str:
        """Zwraca pierwsze 80 znaków opisu zakończone '...' lub pełny opis, jeśli jest krótszy."""
        if len(obj.description) > 80:
            return obj.description[:80] + "..."
        return obj.description

    def get_tags_count(self, obj) -> int:
        """Zwraca liczbę tagów przypisanych do wydarzenia."""
        return obj.tags.count()


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