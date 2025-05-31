from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLES = (
        ('user', 'Обычный пользователь'),
        ('admin', 'Администратор'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')

    objects = CustomUserManager()

    class Meta:
        db_table = 'echo_customuser'

class Album(models.Model):
    artist = models.CharField(max_length=100, verbose_name="Исполнитель")
    title = models.CharField(max_length=200, verbose_name="Название альбома")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена")
    release_year = models.IntegerField(verbose_name="Год выпуска")

    def __str__(self):
        return f"{self.artist} - {self.title} ({self.release_year})"

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.album.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def total_price(self):
        return self.price * self.quantity
