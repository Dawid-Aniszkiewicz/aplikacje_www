from decimal import Decimal
from events.models import Event

# 1. Wszystkie opublikowane wydarzenia, chronologicznie
#    (kolejność wynika z Meta ordering = ['date'] w modelu Event, Lab 2 Krok 1)
for event in Event.objects.filter(is_published=True):
    print(event)

# 2. Wydarzenia z limitem miejsc co najmniej 50
#    (operator __gte nie występuje w Kroku 5, tylko __gt i __icontains)
for event in Event.objects.filter(capacity__gte=50):
    print(f"{event.title} - {event.capacity} miejsc")

# 3. Łączna liczba darmowych wydarzeń
print(Event.objects.filter(price=Decimal('0.00')).count())

# 4. Zmiana is_published z True na False i zapis w bazie
event = Event.objects.get(id=1)
event.is_published = False
event.save()