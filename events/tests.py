from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Event


class EventHubTemplateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('org', password='x')
        cls.tech = Category.objects.create(name='Technologia', slug='technologia')
        cls.biz = Category.objects.create(name='Biznes', slug='biznes')

        def make(title, slug, cat, published=True, days=5):
            return Event.objects.create(
                title=title, slug=slug, category=cat, organizer=cls.user,
                description='Opis wydarzenia ' * 10, location='Olsztyn',
                date=timezone.now() + timedelta(days=days),
                capacity=50, price=0, is_published=published,
            )

        cls.e1 = make('Warsztaty Django', 'warsztaty-django', cls.tech)
        cls.e2 = make('Konferencja Python', 'konferencja-python', cls.tech)
        cls.e3 = make('Meetup Linux', 'meetup-linux', cls.tech)
        cls.e4 = make('Hackathon', 'hackathon', cls.tech)
        cls.e5 = make('Ukryte', 'ukryte', cls.tech, published=False)
        cls.b1 = make('Targi Biznesu', 'targi-biznesu', cls.biz)

    # --- Zadanie 1 i 5: szablony, include, timeuntil ---
    def test_list_uses_templates_and_include(self):
        r = self.client.get(reverse('events:event-list'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'events/base.html')
        self.assertTemplateUsed(r, 'events/event_list.html')
        self.assertTemplateUsed(r, 'events/includes/event_card.html')

    def test_list_shows_only_published(self):
        r = self.client.get(reverse('events:event-list'))
        self.assertContains(r, 'Warsztaty Django')
        self.assertNotContains(r, 'Ukryte')

    def test_card_shows_timeuntil(self):
        r = self.client.get(reverse('events:event-list'))
        self.assertContains(r, '⏳ Za')

    # --- Zadanie 2: menu kategorii ---
    def test_categories_in_context_and_links(self):
        r = self.client.get(reverse('events:event-list'))
        self.assertEqual(r.context['categories'].count(), 2)
        self.assertContains(r, reverse('events:events-by-category', args=['biznes']))
        self.assertContains(r, 'Wszystkie')

    def test_filter_by_category(self):
        r = self.client.get(reverse('events:events-by-category', args=['biznes']))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Targi Biznesu')
        self.assertNotContains(r, 'Warsztaty Django')
        self.assertEqual(r.context['current_category'], self.biz)
        self.assertEqual(r.context['categories'].count(), 2)

    def test_active_category_highlighted(self):
        r = self.client.get(reverse('events:events-by-category', args=['biznes']))
        self.assertContains(r, 'class="active"', count=1)

    def test_all_link_active_on_main_list(self):
        r = self.client.get(reverse('events:event-list'))
        self.assertContains(r, 'class="active"', count=1)

    def test_unknown_category_404(self):
        r = self.client.get(reverse('events:events-by-category', args=['brak']))
        self.assertEqual(r.status_code, 404)

    # --- Zadanie 3: wyszukiwarka ---
    def test_search_filters_by_title(self):
        r = self.client.get(reverse('events:event-list'), {'q': 'django'})
        self.assertContains(r, 'Warsztaty Django')
        self.assertNotContains(r, 'Konferencja Python')

    def test_search_keeps_phrase_in_input(self):
        r = self.client.get(reverse('events:event-list'), {'q': 'django'})
        self.assertEqual(r.context['q'], 'django')
        self.assertContains(r, 'value="django"')

    def test_search_empty_q_returns_all(self):
        r = self.client.get(reverse('events:event-list'), {'q': ''})
        self.assertEqual(len(r.context['events']), 5)

    def test_search_no_results(self):
        r = self.client.get(reverse('events:event-list'), {'q': 'xyzxyz'})
        self.assertContains(r, 'Brak opublikowanych wydarzeń')

    # --- Zadanie 4: podobne wydarzenia ---
    def test_related_events_max3_same_category_excludes_current(self):
        r = self.client.get(reverse('events:event-detail', args=[self.e1.slug]))
        related = list(r.context['related_events'])
        self.assertEqual(len(related), 3)
        self.assertNotIn(self.e1, related)
        self.assertNotIn(self.e5, related)   # nieopublikowane
        self.assertNotIn(self.b1, related)   # inna kategoria
        self.assertTrue(all(e.category == self.tech for e in related))

    def test_related_events_empty_message(self):
        r = self.client.get(reverse('events:event-detail', args=[self.b1.slug]))
        self.assertEqual(len(r.context['related_events']), 0)
        self.assertContains(r, 'Brak innych wydarzeń w tej kategorii')

    def test_detail_404_for_unpublished_and_unknown(self):
        self.assertEqual(
            self.client.get(reverse('events:event-detail', args=['ukryte'])).status_code, 404)
        self.assertEqual(
            self.client.get(reverse('events:event-detail', args=['nie-ma'])).status_code, 404)