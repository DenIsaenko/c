from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission


class Avatar(models.Model):
    """Модель для хранения аватара пользователя"""

    src = models.ImageField(
        upload_to=r"myauth\avatars\user_avatars",
        default="myauth/avatars/default.png",
        verbose_name="Ссылка",
    )
    alt = models.CharField(max_length=128, default="avatar", verbose_name="Описание")

    class Meta:
        verbose_name = "Аватар"
        verbose_name_plural = "Аватары"


class Profile(models.Model):
    """Модель профиля пользователя"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    fullName = models.CharField(max_length=128, verbose_name="Полное имя")
    phone = models.PositiveIntegerField(
        blank=True, null=True, unique=True, verbose_name="Номер телефона"
    )
    balance = models.DecimalField(
        decimal_places=2, max_digits=10, default=0, verbose_name="Баланс"
    )
    avatar = models.ForeignKey(
        Avatar,
        on_delete=models.CASCADE,
        related_name="profiles",
        verbose_name="Аватар",
    )
    email = models.EmailField(default="")
