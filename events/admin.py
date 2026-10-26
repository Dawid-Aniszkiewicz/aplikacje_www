from django.contrib import admin
from .models import Category, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'events_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    # Dekorator @admin.display formatuje niestandardowe kolumny na liście rekordów
    @admin.display(description="Liczba wydarzeń")
    def events_count(self, obj):
        return obj.events.count()


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organizer', 'date', 'price', 'capacity', 'is_published')
    list_filter = ('category', 'is_published', 'date')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'price')
    date_hierarchy = 'date'
    ordering = ('date',)

    fieldsets = (
        ("Podstawowe informacje", {
            'fields': ('title', 'slug', 'category', 'organizer', 'description')
        }),
        ("Szczegóły organizacyjne", {
            'fields': ('location', 'date', 'capacity', 'price', 'is_published')
        }),
    )