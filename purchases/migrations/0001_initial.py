import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('slug', models.SlugField(unique=True)),
                ('icon', models.CharField(default='bi-tag', max_length=50, verbose_name='Иконка Bootstrap')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='purchases/', verbose_name='Изображение')),
                ('status', models.CharField(
                    choices=[
                        ('collecting', 'Сбор заявок'), ('processing', 'Обработка'),
                        ('ordered', 'Заказ оформлен'), ('delivered', 'Доставлено на склад'),
                        ('completed', 'Завершена'), ('cancelled', 'Отменена'),
                    ],
                    default='collecting', max_length=20, verbose_name='Статус'
                )),
                ('min_participants', models.PositiveIntegerField(default=1, verbose_name='Мин. участников')),
                ('max_participants', models.PositiveIntegerField(blank=True, null=True, verbose_name='Макс. участников')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за единицу')),
                ('organizer_fee', models.DecimalField(decimal_places=2, default=5.0, max_digits=4, verbose_name='Комиссия орг-ра (%)')),
                ('stop_date', models.DateTimeField(verbose_name='Дата окончания сбора')),
                ('delivery_date', models.DateTimeField(blank=True, null=True, verbose_name='Ожидаемая дата доставки')),
                ('delivery_address', models.CharField(blank=True, max_length=500, verbose_name='Адрес выдачи')),
                ('source_url', models.URLField(blank=True, verbose_name='Ссылка на товар')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='purchases', to='purchases.category', verbose_name='Категория'
                )),
                ('organizer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='organized_purchases',
                    to=settings.AUTH_USER_MODEL, verbose_name='Организатор'
                )),
            ],
            options={
                'verbose_name': 'Закупка',
                'verbose_name_plural': 'Закупки',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Ожидает подтверждения'), ('confirmed', 'Подтверждён'),
                        ('paid', 'Оплачен'), ('received', 'Получен'), ('cancelled', 'Отменён'),
                    ],
                    default='pending', max_length=20, verbose_name='Статус'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purchase', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='orders', to='purchases.purchase', verbose_name='Закупка'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'
                )),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'ordering': ['-created_at'],
                'unique_together': {('purchase', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL, verbose_name='Автор'
                )),
                ('purchase', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments', to='purchases.purchase', verbose_name='Закупка'
                )),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_at'],
            },
        ),
    ]
