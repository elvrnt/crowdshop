from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View, TemplateView
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .models import Purchase, Order, Comment, Category
from .forms import PurchaseForm, OrderForm, CommentForm, PurchaseFilterForm


class HomeView(ListView):
    model = Purchase
    template_name = 'purchases/home.html'
    context_object_name = 'purchases'
    paginate_by = 6

    def get_queryset(self):
        return Purchase.objects.filter(
            is_active=True, status=Purchase.STATUS_COLLECTING
        ).select_related('organizer', 'category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.annotate(count=Count('purchases')).filter(count__gt=0)
        ctx['total_purchases'] = Purchase.objects.filter(is_active=True).count()
        ctx['total_users'] = Purchase.objects.values('organizer').distinct().count()
        return ctx


class PurchaseListView(ListView):
    model = Purchase
    template_name = 'purchases/list.html'
    context_object_name = 'purchases'
    paginate_by = 9

    def get_queryset(self):
        qs = Purchase.objects.filter(is_active=True).select_related('organizer', 'category')
        form = PurchaseFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('q'):
                qs = qs.filter(
                    Q(title__icontains=form.cleaned_data['q']) |
                    Q(description__icontains=form.cleaned_data['q'])
                )
            if form.cleaned_data.get('category'):
                qs = qs.filter(category=form.cleaned_data['category'])
            if form.cleaned_data.get('status'):
                qs = qs.filter(status=form.cleaned_data['status'])
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = PurchaseFilterForm(self.request.GET)
        ctx['categories'] = Category.objects.all()
        return ctx


class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'purchases/detail.html'
    context_object_name = 'purchase'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        purchase = self.get_object()
        ctx['comment_form'] = CommentForm()
        ctx['comments'] = purchase.comments.select_related('author').all()
        ctx['orders'] = purchase.orders.filter(
            status__in=['confirmed', 'paid', 'received']
        ).select_related('user')[:10]

        if self.request.user.is_authenticated:
            ctx['user_order'] = Order.objects.filter(
                purchase=purchase, user=self.request.user
            ).first()
            ctx['order_form'] = OrderForm()
        return ctx


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchases/form.html'

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        purchase = form.save()
        self.request.user.total_purchases += 1
        self.request.user.save(update_fields=['total_purchases'])
        messages.success(self.request, f'Закупка «{purchase.title}» успешно создана!')
        return redirect(reverse('purchases:detail', kwargs={'pk': purchase.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Создать закупку'
        ctx['btn_text'] = 'Создать'
        return ctx


class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchases/form.html'

    def dispatch(self, request, *args, **kwargs):
        purchase = self.get_object()
        if purchase.organizer != request.user and not request.user.is_staff:
            messages.error(request, 'У вас нет прав для редактирования этой закупки.')
            return redirect('purchases:detail', pk=purchase.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('purchases:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Закупка успешно обновлена.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Редактировать закупку'
        ctx['btn_text'] = 'Сохранить'
        return ctx


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)

        if not purchase.is_open:
            messages.error(request, 'Сбор заявок на эту закупку уже завершён.')
            return redirect('purchases:detail', pk=pk)

        if Order.objects.filter(purchase=purchase, user=request.user).exists():
            messages.warning(request, 'Вы уже участвуете в этой закупке.')
            return redirect('purchases:detail', pk=pk)

        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.purchase = purchase
            order.user = request.user
            order.save()
            messages.success(request, f'Заявка на «{purchase.title}» успешно подана!')
        else:
            messages.error(request, 'Ошибка при подаче заявки. Проверьте данные.')
        return redirect('purchases:detail', pk=pk)


class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status in ('pending', 'confirmed'):
            order.status = Order.STATUS_CANCELLED
            order.save()
            messages.success(request, 'Заявка отменена.')
        else:
            messages.error(request, 'Невозможно отменить заявку в текущем статусе.')
        return redirect('purchases:detail', pk=order.purchase.pk)


class UpdateOrderStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        purchase = order.purchase

        if purchase.organizer != request.user and not request.user.is_staff:
            messages.error(request, 'Нет прав.')
            return redirect('purchases:detail', pk=purchase.pk)

        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заявки обновлён: {order.status_label}')
        return redirect('purchases:manage', pk=purchase.pk)


class UpdatePurchaseStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)
        if purchase.organizer != request.user and not request.user.is_staff:
            messages.error(request, 'Нет прав.')
            return redirect('purchases:detail', pk=pk)

        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Purchase.STATUS_CHOICES]
        if new_status in valid_statuses:
            purchase.status = new_status
            purchase.save()
            messages.success(request, f'Статус закупки изменён на: {purchase.status_label}')
        return redirect('purchases:manage', pk=pk)


class PurchaseManageView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'purchases/manage.html'
    context_object_name = 'purchase'

    def dispatch(self, request, *args, **kwargs):
        purchase = self.get_object()
        if purchase.organizer != request.user and not request.user.is_staff:
            messages.error(request, 'Нет доступа к управлению этой закупкой.')
            return redirect('purchases:detail', pk=purchase.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        purchase = self.get_object()
        ctx['orders'] = purchase.orders.select_related('user').order_by('-created_at')
        ctx['status_choices'] = Purchase.STATUS_CHOICES
        ctx['order_status_choices'] = Order.STATUS_CHOICES
        total = purchase.orders.filter(
            status__in=['confirmed', 'paid', 'received']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        ctx['total_units'] = total
        return ctx


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.purchase = purchase
            comment.author = request.user
            comment.save()
        return redirect(reverse('purchases:detail', kwargs={'pk': pk}) + '#comments')


class MyCatalogView(LoginRequiredMixin, TemplateView):
    template_name = 'purchases/my_catalog.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['my_purchases'] = Purchase.objects.filter(
            organizer=self.request.user
        ).order_by('-created_at')
        ctx['my_orders'] = Order.objects.filter(
            user=self.request.user
        ).select_related('purchase', 'purchase__organizer').order_by('-created_at')
        return ctx
