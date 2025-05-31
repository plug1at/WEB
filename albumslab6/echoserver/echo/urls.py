from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import change_password

urlpatterns = [
    # Основные маршруты
    path('', views.album_list, name='album_list'),
    path('new/', views.album_new, name='album_new'),
    path('<int:pk>/edit/', views.album_edit, name='album_edit'),
    path('<int:pk>/delete/', views.album_delete, name='album_delete'),

    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='album_list'), name='logout'),
    path('profile/change-password/', change_password, name='change_password'),
    path('check_email/', views.check_email, name='check_email'),

    # Профиль
    path('profile/', views.profile, name='profile'),

    # Корзина
    path('cart/add/<int:album_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),

    # Заказы
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]