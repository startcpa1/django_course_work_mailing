import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from mailing.models import NULLABLE


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Почта')

    phone = models.CharField(max_length=35, verbose_name='Телефон', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', **NULLABLE)
    verify_code = models.UUIDField(default=uuid.uuid4, verbose_name='Код вeрификации', editable=False)
    is_verified = models.BooleanField(default=False, verbose_name='Верификация')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
