from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Album, CustomUser, Cart, CartItem, Order, OrderItem
from .forms import AlbumForm, CustomUserCreationForm, ProfileForm, CartItemForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomPasswordChangeForm
from django.http import JsonResponse


def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)


def check_email(request):
    email = request.GET.get('email', '')
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


def album_list(request):
    albums = Album.objects.all().order_by('artist', 'title')

    # Фильтрация по году выпуска
    release_year = request.GET.get('release_year')
    if release_year:
        albums = albums.filter(release_year=release_year)

    # Фильтрация по цене
    max_price = request.GET.get('max_price')
    if max_price:
        albums = albums.filter(price__lte=max_price)

    paginator = Paginator(albums, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем уникальные года для фильтра (исправленная версия)
    years = Album.objects.values_list('release_year', flat=True).order_by('release_year').distinct()

    return render(request, 'albums/album_list.html', {
        'page_obj': page_obj,
        'user': request.user,
        'years': years,
    })


@login_required
@user_passes_test(is_admin)
def album_new(request):
    if request.method == "POST":
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save()
            messages.success(request, f'Альбом "{album.title}" успешно добавлен')
            return redirect('album_list')
    else:
        form = AlbumForm()
    return render(request, 'albums/album_edit.html', {
        'form': form,
        'title': 'Новый альбом'
    })


@login_required
@user_passes_test(is_admin)
def album_edit(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if request.method == "POST":
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, f'Альбом "{album.title}" успешно обновлен')
            return redirect('album_list')
    else:
        form = AlbumForm(instance=album)
    return render(request, 'albums/album_edit.html', {
        'form': form,
        'title': f'Редактирование: {album.title}'
    })


@login_required
@user_passes_test(is_admin)
def album_delete(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if request.method == "POST":
        title = album.title
        album.delete()
        messages.success(request, f'Альбом "{title}" успешно удален')
        return redirect('album_list')
    return render(request, 'albums/album_confirm_delete.html', {'album': album})


# Аутентификация
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('album_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('album_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
    return redirect('album_list')



@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно обновлены')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'registration/profile.html', {'form': form})



@login_required
def add_to_cart(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        album=album,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'Альбом "{album.title}" добавлен в корзину')
    return redirect('album_list')


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/view_cart.html', {'cart': cart})


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Количество обновлено')
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('view_cart')



@login_required
@transaction.atomic
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Ваша корзина пуста')
        return redirect('view_cart')

    order = Order.objects.create(
        user=request.user,
        total_price=cart.total_price()
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            album=item.album,
            quantity=item.quantity,
            price=item.album.price
        )

    cart.items.all().delete()
    messages.success(request, 'Заказ успешно оформлен')
    return redirect('order_detail', order_id=order.id)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем сессию, чтобы пользователь не разлогинился
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'registration/change_password.html', {
        'form': form,
        'title': 'Изменение пароля'
    })


