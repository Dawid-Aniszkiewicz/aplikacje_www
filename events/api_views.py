from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Event, Category, Tag
from .serializers import EventModelSerializer, CategorySerializer, TagSerializer


@api_view(['GET', 'POST'])
def event_list_create_api(request):
    """
    GET: Zwraca listę wydarzeń (opcjonalnie przefiltrowanych po kategorii).
    POST: Tworzy nowe wydarzenie po przejściu walidacji.
    """
    if request.method == 'GET':
        events = Event.objects.select_related('category', 'organizer').prefetch_related('tags').all()

        category_id = request.query_params.get('category')
        if category_id:
            events = events.filter(category_id=category_id)

        tag_slug = request.query_params.get('tag')
        if tag_slug:
            events = events.filter(tags__slug=tag_slug)

        free = request.query_params.get('free')
        if free and free.lower() == 'true':
            events = events.filter(price=0)

        serializer = EventModelSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EventModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def event_detail_api(request, pk):
    """
    GET: Szczegóły pojedynczego wydarzenia.
    PUT: Pełna aktualizacja wydarzenia (wymaga wszystkich pól wymaganych).
    PATCH: Częściowa aktualizacja wybranych pól wydarzenia (partial=True).
    DELETE: Usunięcie wydarzenia.
    """
    queryset = Event.objects.select_related('category', 'organizer').prefetch_related('tags')
    event = get_object_or_404(queryset, pk=pk)

    if request.method == 'GET':
        serializer = EventModelSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = EventModelSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = EventModelSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def category_list_api(request):
    """Zwraca listę wszystkich kategorii z liczbą powiązanych wydarzeń."""
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def category_detail_api(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if category.events.exists():
            return Response(
                {"error": "Nie można usunąć kategorii, do której są przypisane wydarzenia."},
                status=status.HTTP_400_BAD_REQUEST
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def tag_list_create_api(request):
    if request.method == 'GET':
        tags = Tag.objects.order_by('name')
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)