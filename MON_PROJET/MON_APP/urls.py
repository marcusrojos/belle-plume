from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('panier/', views.panier, name='panier'),
    path('favoris/', views.favoris, name='favoris'),
    path('profil/', views.profil, name='profil'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/toggle/', views.admin_user_toggle, name='admin_user_toggle'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/books/', views.admin_books, name='admin_books'),
    path('admin/books/<int:book_id>/edit/', views.admin_book_edit, name='admin_book_edit'),
    path('admin/books/<int:book_id>/delete/', views.admin_book_delete, name='admin_book_delete'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('admin/sales-data/', views.admin_sales_data, name='admin_sales_data'),
    # Actions
    path('favorite/toggle/<int:book_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('admin/order/<int:order_id>/status/', views.admin_update_order_status, name='admin_update_order_status'),
    path('book/<int:book_id>/rate/', views.rate_book, name='rate_book'),
    path('book/<int:book_id>/comment/', views.comment_book, name='comment_book'),
    path('book/<int:book_id>/meta/', views.book_meta, name='book_meta'),
]