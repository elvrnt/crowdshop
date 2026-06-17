from django import forms
from .models import Purchase, Order, Comment


class PurchaseForm(forms.ModelForm):
    stop_date = forms.DateTimeField(
        label='Дата окончания сбора',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    delivery_date = forms.DateTimeField(
        label='Ожидаемая дата доставки',
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Purchase
        fields = [
            'title', 'description', 'category', 'image',
            'price_per_unit', 'organizer_fee', 'min_participants', 'max_participants',
            'stop_date', 'delivery_date', 'delivery_address', 'source_url',
        ]
        labels = {
            'title': 'Название закупки',
            'description': 'Описание',
            'category': 'Категория',
            'image': 'Фото товара',
            'price_per_unit': 'Цена за единицу (руб.)',
            'organizer_fee': 'Комиссия организатора (%)',
            'min_participants': 'Минимум участников',
            'max_participants': 'Максимум участников',
            'delivery_address': 'Адрес выдачи',
            'source_url': 'Ссылка на товар',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('stop_date', 'delivery_date'):
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs['class'] = 'form-control'

        if self.instance and self.instance.pk:
            if self.instance.stop_date:
                self.initial['stop_date'] = self.instance.stop_date.strftime('%Y-%m-%dT%H:%M')
            if self.instance.delivery_date:
                self.initial['delivery_date'] = self.instance.delivery_date.strftime('%Y-%m-%dT%H:%M')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'comment']
        labels = {
            'quantity': 'Количество единиц',
            'comment': 'Комментарий (например, размер, цвет)',
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите комментарий...',
            }),
        }


class PurchaseFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Поиск', widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Поиск закупок...'
    }))
    category = forms.ModelChoiceField(
        queryset=None, required=False, empty_label='Все категории',
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + Purchase.STATUS_CHOICES,
        required=False, label='Статус',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.all()
