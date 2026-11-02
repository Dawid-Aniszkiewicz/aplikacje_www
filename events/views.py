from django.shortcuts import render, get_object_or_404
from .models import Event, Category


def event_list(request):
    """Widok listy opublikowanych wydarzeń."""
    events = Event.objects.filter(is_published=True).select_related('category', 'organizer')

    q = request.GET.get('q')
    if q:
        events = events.filter(title__icontains=q)

    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': Category.objects.all(),
        'q': q,
    })


def event_detail(request, slug):
    """Widok pojedynczego wydarzenia na podstawie parametru slug."""
    event = get_object_or_404(
        Event.objects.select_related('category', 'organizer'),
        slug=slug,
        is_published=True
    )
    related_events = (
        Event.objects
        .filter(category=event.category, is_published=True)
        .exclude(id=event.id)[:3]
    )
    return render(request, 'events/event_detail.html', {
        'event': event,
        'related_events': related_events,
    })


def events_by_category(request, category_slug):
    """Wydarzenia przefiltrowane według kategorii."""
    category = get_object_or_404(Category, slug=category_slug)
    events = category.events.filter(is_published=True).select_related('organizer')
    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': Category.objects.all(),
        'current_category': category,
    })