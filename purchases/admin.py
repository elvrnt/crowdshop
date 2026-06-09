from django.contrib import admin
from .models import Category, Purchase, Order, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'status', 'price_per_unit', 'stop_date', 'is_active')
    list_filter = ('status', 'category', 'is_active')
    search_fields = ('title', 'organizer__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'is_active')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'purchase', 'quantity', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'purchase__title')
    list_editable = ('status',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'purchase', 'text', 'created_at')
    list_filter = ('created_at',)
