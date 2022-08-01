from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# сделать class Roles(models.TextChoices) невозможно,
# ввиду того, что TextChoices отсутствует в текущей версии django
ROLES = (
    ('user', 'user'),
    ('moderator', 'moderator'),
    ('admin', 'admin'),
)

MINVALIDATORERROR = 'Оценка не может быть меньше 1'
MAXVALIDATORERROR = 'Оценка не может быть больше 10'


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(max_length=100, choices=ROLES, default='user')

    class Meta:
        ordering = ['id']


class Genre(models.Model):
    name = models.TextField('Название жанра', max_length=256)
    slug = models.SlugField(
        'Адрес жанра',
        unique=True,
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.TextField('Название категории', max_length=256)
    slug = models.SlugField(
        'Адрес категории',
        unique=True,
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField('Название произведения', max_length=200)
    description = models.TextField('Описание произведения', blank=True)
    year = models.PositiveSmallIntegerField(
        'Год издания произведения',
        blank=True,
        null=False,
        db_index=True,
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='c_titles',
        blank=False, null=True,
        verbose_name='Категория', help_text='Выберите категорию произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='g_titles',
        verbose_name='Жанры',
    )

    def __str__(self):
        return self.name[:100]


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Произведение',
    )
    text = models.TextField('Текст отзывы', max_length=500)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(0, message=MINVALIDATORERROR),
            MaxValueValidator(10, message=MAXVALIDATORERROR)
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:100]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария', max_length=200)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
