from django.db import models
from django.db.models.functions import datetime
from config import settings

NULLABLE = {'null': True, 'blank': True}


class Client(models.Model):
    """Кто получает рассылку"""
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    surname = models.CharField(max_length=50, verbose_name='Отчество', **NULLABLE)
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Почта', unique=True)
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Владелец', **NULLABLE)

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.email})'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('last_name', 'first_name')


class Message(models.Model):
    """Сообщение рассылки"""
    title = models.CharField(max_length=100, verbose_name='Тема письма', default='Без темы')
    text = models.TextField(verbose_name='Содержание', **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('title',)


class Mailing(models.Model):
    """Настройки рассылки"""
    """Статусы рассылки"""
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]
    """Периодичность рассылки"""
    PERIOD_CHOICES = [
        ('once', '1 раз'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
    ]

    start_point = models.DateTimeField(verbose_name='Начать рассылку', default=datetime.datetime.now)
    stop_point = models.DateTimeField(verbose_name='Завершить рассылку', default=datetime.datetime.now)
    period = models.CharField(max_length=20, verbose_name='Периодичность', choices=PERIOD_CHOICES, default='once')
    status = models.CharField(max_length=20, verbose_name='Статус выполнения', choices=STATUS_CHOICES,
                              default='created')

    client = models.ManyToManyField(Client, verbose_name='Клиенты рассылки')
    message = models.ForeignKey(Message, verbose_name='Сообщение', on_delete=models.CASCADE, **NULLABLE)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name='Владелец',
                              **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Активная')

    def __str__(self):
        return f'Начало {self.start_point}, повтор {self.period}, статус {self.status} '

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ('set_is_active', 'Изменить aктивность'),
        ]


class Log(models.Model):
    """Логи рассылки"""
    """Статус рассылки для лога"""
    LOG_CHOICES = [
        (True, 'Успешно'),
        (False, 'Ошибка')
    ]
    attempt_time = models.DateTimeField(verbose_name='Дата и время последней попытки', **NULLABLE)
    attempt_status = models.CharField(max_length=10, verbose_name='Статус попытки', choices=LOG_CHOICES, default=True)
    server_response = models.TextField(verbose_name='Ответ почтового сервера', **NULLABLE)

    mailing = models.ForeignKey(Mailing, verbose_name='Рассылка', on_delete=models.CASCADE, **NULLABLE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='клиент рассылки', **NULLABLE)

    def __str__(self):
        return f'Попытка отправки {self.attempt_time}, статус - {self.attempt_status}'

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
