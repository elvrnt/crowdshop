from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField('Иконка Bootstrap', max_length=50, default='bi-tag')
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_COLLECTING = 'collecting'
    STATUS_PROCESSING = 'processing'
    STATUS_ORDERED = 'ordered'
    STATUS_DELIVERED = 'delivered'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_COLLECTING, 'Сбор заявок'),
        (STATUS_PROCESSING, 'Обработка'),
        (STATUS_ORDERED, 'Заказ оформлен'),
        (STATUS_DELIVERED, 'Доставлено на склад'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_CANCELLED, 'Отменена'),
    ]

    STATUS_COLORS = {
        STATUS_COLLECTING: 'success',
        STATUS_PROCESSING: 'warning',
        STATUS_ORDERED: 'info',
        STATUS_DELIVERED: 'primary',
        STATUS_COMPLETED: 'secondary',
        STATUS_CANCELLED: 'danger',
    }

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_purchases',
        verbose_name='Организатор'
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='purchases', verbose_name='Категория'
    )
    image = models.ImageField('Изображение', upload_to='purchases/', blank=True, null=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_COLLECTING)
    min_participants = models.PositiveIntegerField('Мин. участников', default=1)
    max_participants = models.PositiveIntegerField('Макс. участников', null=True, blank=True)
    price_per_unit = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)
    organizer_fee = models.DecimalField('Комиссия орг-ра (%)', max_digits=4, decimal_places=2, default=5.00)
    stop_date = models.DateTimeField('Дата окончания сбора')
    delivery_date = models.DateTimeField('Ожидаемая дата доставки', null=True, blank=True)
    delivery_address = models.CharField('Адрес выдачи', max_length=500, blank=True)
    source_url = models.URLField('Ссылка на товар', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Закупка'
        verbose_name_plural = 'Закупки'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def participants_count(self):
        return self.orders.filter(status__in=['confirmed', 'paid', 'received']).values('user').distinct().count()

    @property
    def total_units(self):
        from django.db.models import Sum
        result = self.orders.filter(
            status__in=['confirmed', 'paid', 'received']
        ).aggregate(total=Sum('quantity'))
        return result['total'] or 0

    @property
    def is_open(self):
        return self.status == self.STATUS_COLLECTING and self.stop_date > timezone.now()

    @property
    def price_with_fee(self):
        return self.price_per_unit * (1 + self.organizer_fee / 100)

    @property
    def days_left(self):
        if self.stop_date > timezone.now():
            delta = self.stop_date - timezone.now()
            return delta.days
        return 0


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PAID = 'paid'
    STATUS_RECEIVED = 'received'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает подтверждения'),
        (STATUS_CONFIRMED, 'Подтверждён'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_RECEIVED, 'Получен'),
        (STATUS_CANCELLED, 'Отменён'),
    ]

    STATUS_COLORS = {
        STATUS_PENDING: 'warning',
        STATUS_CONFIRMED: 'info',
        STATUS_PAID: 'success',
        STATUS_RECEIVED: 'primary',
        STATUS_CANCELLED: 'danger',
    }

    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Закупка'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Пользователь'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        unique_together = ('purchase', 'user')

    def __str__(self):
        return f'{self.user} — {self.purchase} x{self.quantity}'

    @property
    def total_price(self):
        return self.purchase.price_with_fee * self.quantity

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class Comment(models.Model):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Закупка'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Текст')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.text[:50]}'
