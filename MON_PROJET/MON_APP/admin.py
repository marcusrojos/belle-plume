from django.contrib import admin
from .models import Book, CartItem, Order, OrderItem, Favorite, Rating, Comment


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'price')
	search_fields = ('title', 'author')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ('user', 'book', 'quantity')
	list_filter = ('user',)


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'total', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	inlines = [OrderItemInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
	list_display = ('user', 'book')
	search_fields = ('user__username', 'book__title')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
	list_display = ('user', 'book', 'stars', 'created_at')
	list_filter = ('stars',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('user', 'book', 'created_at')
	search_fields = ('text', 'user__username', 'book__title')

