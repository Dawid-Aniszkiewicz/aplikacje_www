from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa kategorii")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug (URL)")
    description = models.TextField(blank=True, verbose_name="Opis kategorii")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tytuł wydarzenia")
    slug = models.SlugField(max_length=220, unique=True, verbose_name="Slug (URL)")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Kategoria"
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_events",
        verbose_name="Organizator"
    )
    description = models.TextField(verbose_name="Szczegółowy opis")
    location = models.CharField(max_length=255, verbose_name="Miejsce / Adres / Link online")
    date = models.DateTimeField(verbose_name="Data i godzina rozpoczęcia")
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Maksymalna liczba uczestników"
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        verbose_name="Cena biletu (PLN)"
    )
    is_published = models.BooleanField(default=True, verbose_name="Opublikowane")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ostatnia aktualizacja")

    class Meta:
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%Y-%m-%d %H:%M')})"