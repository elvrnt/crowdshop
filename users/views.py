from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, View
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Добро пожаловать, {user.first_name}! Регистрация прошла успешно.')
        return redirect(self.success_url)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class LoginView(View):
    template_name = 'users/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        from django.shortcuts import render
        form = LoginForm(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        from django.shortcuts import render
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'С возвращением, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'Вы вышли из системы.')
        return redirect('home')


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from purchases.models import Purchase, Order
        ctx['my_purchases'] = Purchase.objects.filter(organizer=self.request.user).order_by('-created_at')[:5]
        ctx['my_orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлён.')
        return super().form_valid(form)


class PublicProfileView(DetailView):
    model = User
    template_name = 'users/public_profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from purchases.models import Purchase
        ctx['purchases'] = Purchase.objects.filter(
            organizer=self.get_object(), is_active=True
        ).order_by('-created_at')[:10]
        return ctx
