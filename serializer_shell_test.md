>>> import io
>>> from events.models import Event
>>> from events.serializers import EventSerializer
>>> from rest_framework.renderers import JSONRenderer
>>> 
>>> event = Event.objects.first()
>>> serializer = EventSerializer(event)
>>> print(serializer.data)
{'id': 2, 'title': 'W2', 'slug': 'w2', 'category_id': 2, 'organizer_id': 1, 'description': 'w2', 'location': 'a2', 'date': '2026-10-26T23:33:13Z', 'capacity': 2, 'price': '0.00', 'is_published': False, 'created_at': '2026-10-26T23:33:14.814508Z'}
>>> 
>>> json_bytes = JSONRenderer().render(serializer.data)
>>> print(json_bytes)
b'{"id":2,"title":"W2","slug":"w2","category_id":2,"organizer_id":1,"description":"w2","location":"a2","date":"2026-10-26T23:33:13Z","capacity":2,"price":"0.00","is_published":false,"created_at":"2026-10-26T23:33:14.814508Z"}' 

>>> from rest_framework.parsers import JSONParser
>>> from django.contrib.auth.models import User
>>> from events.models import Category
>>> 
>>> stream = io.BytesIO(json_bytes)
>>> data = JSONParser().parse(stream)
>>> 
>>> data['title'] = "Nowe Warsztaty Pythona"
>>> data['slug'] = "nowe-warsztaty-pythona-2"
>>> 
>>> deserializer = EventSerializer(data=data)
>>> 
>>> if deserializer.is_valid():
...     print("Dane są poprawne!")
...     print(deserializer.validated_data)
...     new_event = deserializer.save()
...     print(f"Utworzono wydarzenie o id={new_event.id}")
... else:
...     print("Błędy walidacji:", deserializer.errors)
... 
Dane są poprawne!
{'title': 'Nowe Warsztaty Pythona', 'slug': 'nowe-warsztaty-pythona-2', 'category': <Category: Kat2>, 'organizer': <User: admin>, 'description': 'w2', 'location': 'a2', 'date': datetime.datetime(2026, 10, 26, 23, 33, 13, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'capacity': 2, 'price': Decimal('0.00'), 'is_published': False}
Utworzono wydarzenie o id=5

>>> invalid_data = {
...     'title': '',
...     'capacity': -5,
...     'date': '15-12-2026 godz. 10'
... }
>>> bad_serializer = EventSerializer(data=invalid_data)
>>> print("Czy poprawne?", bad_serializer.is_valid())
Czy poprawne? False
>>> print("Błędy:", bad_serializer.errors)
Błędy: {'title': [ErrorDetail(string='This field may not be blank.', code='blank')], 'slug': [ErrorDetail(string='This field is required.', code='required')], 'category_id': [ErrorDetail(string='This field is required.', code='required')], 'organizer_id': [ErrorDetail(string='This field is required.', code='required')], 'description': [ErrorDetail(string='This field is required.', code='required')], 'location': [ErrorDetail(string='This field is required.', code='required')], 'date': [ErrorDetail(string='Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].', code='invalid')], 'capacity': [ErrorDetail(string='Ensure this value is greater than or equal to 1.', code='min_value')]}
>>> 