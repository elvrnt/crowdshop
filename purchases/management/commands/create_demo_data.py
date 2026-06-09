import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Создаёт демо-данные для разработки'

    def handle(self, *args, **kwargs):
        from users.models import User
        from purchases.models import Category, Purchase, Order

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@crowdshop.ru',
                password='admin123',
                first_name='Администратор',
                last_name='Системы',
            )
            self.stdout.write(self.style.SUCCESS('✓ Суперпользователь создан (admin / admin123)'))

        # Demo organizer
        organizer, created = User.objects.get_or_create(
            username='organizer',
            defaults={
                'email': 'organizer@crowdshop.ru',
                'first_name': 'Мария',
                'last_name': 'Иванова',
                'rating': 4.95,
                'total_purchases': 12,
                'bio': 'Опытный организатор совместных закупок. Работаю с 2020 года.',
            }
        )
        if created:
            organizer.set_password('demo123')
            organizer.save()
            self.stdout.write(self.style.SUCCESS('✓ Демо-организатор создан (organizer / demo123)'))

        # Demo buyer
        buyer, created = User.objects.get_or_create(
            username='buyer',
            defaults={
                'email': 'buyer@crowdshop.ru',
                'first_name': 'Алексей',
                'last_name': 'Петров',
                'rating': 4.80,
            }
        )
        if created:
            buyer.set_password('demo123')
            buyer.save()
            self.stdout.write(self.style.SUCCESS('✓ Демо-покупатель создан (buyer / demo123)'))

        # Categories
        clothing = Category.objects.filter(slug='clothing').first()
        electronics = Category.objects.filter(slug='electronics').first()
        kids = Category.objects.filter(slug='kids').first()

        # Demo purchases
        purchases_data = [
            {
                'title': 'Зимние куртки Columbia — унисекс',
                'description': 'Тёплые куртки Columbia на синтепоне. Температурный режим до -25°C.\nДоступные размеры: S, M, L, XL, XXL.\nЦвета: чёрный, тёмно-синий, хаки.\nУкажите в комментарии размер и цвет.',
                'category': clothing,
                'price_per_unit': 4500,
                'organizer_fee': 7,
                'min_participants': 5,
                'stop_date': timezone.now() + timedelta(days=10),
                'delivery_date': timezone.now() + timedelta(days=30),
                'delivery_address': 'г. Москва, ул. Ленина, 10 (ТЦ Центральный, 2 этаж)',
                'source_url': 'https://example.com/columbia-jacket',
            },
            {
                'title': 'Наушники Sony WH-1000XM5',
                'description': 'Беспроводные наушники Sony с шумоподавлением.\nАвтономность до 30 часов.\nBluetooth 5.2, LDAC, поддержка голосовых ассистентов.\nЦвет: чёрный.',
                'category': electronics,
                'price_per_unit': 18000,
                'organizer_fee': 5,
                'min_participants': 3,
                'stop_date': timezone.now() + timedelta(days=7),
                'delivery_date': timezone.now() + timedelta(days=21),
                'delivery_address': 'г. Санкт-Петербург, Невский пр., 55',
            },
            {
                'title': 'Развивающие игрушки Melissa & Doug',
                'description': 'Набор развивающих деревянных игрушек от американского производителя Melissa & Doug.\nВозраст: 2-6 лет.\nЭкологичные материалы, безопасные краски.',
                'category': kids,
                'price_per_unit': 2200,
                'organizer_fee': 8,
                'min_participants': 8,
                'stop_date': timezone.now() + timedelta(days=14),
                'delivery_date': timezone.now() + timedelta(days=35),
                'delivery_address': 'г. Москва, ул. Садовая, 5',
            },
        ]

        for data in purchases_data:
            if not Purchase.objects.filter(title=data['title']).exists():
                purchase = Purchase.objects.create(organizer=organizer, **data)
                # Add a demo order from buyer
                Order.objects.get_or_create(
                    purchase=purchase,
                    user=buyer,
                    defaults={'quantity': 2, 'status': 'confirmed', 'comment': 'Тестовый заказ'}
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Закупка создана: {purchase.title}'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Демо-данные успешно загружены!'))
        self.stdout.write('Учётные записи:')
        self.stdout.write('  admin / admin123  — администратор')
        self.stdout.write('  organizer / demo123 — организатор')
        self.stdout.write('  buyer / demo123   — покупатель')
