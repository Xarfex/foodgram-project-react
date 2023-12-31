# Generated by Django 3.2.3 on 2023-08-15 10:11

import colorfield.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0002_alter_ingredients_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='addingredientinrec',
            options={'verbose_name': 'Количество ингредиента'},
        ),
        migrations.AlterField(
            model_name='addingredientinrec',
            name='amount',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='You can not add less then 1'), django.core.validators.MaxValueValidator(limit_value=1000, message='You can not add more then 1000')]),
        ),
        migrations.AlterField(
            model_name='addingredientinrec',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amounts', to='api.ingredients', verbose_name='Ингридиент'),
        ),
        migrations.AlterField(
            model_name='addingredientinrec',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amounts', to='api.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(help_text='На кого подписываются', on_delete=django.db.models.deletion.CASCADE, related_name='who_are_subscribed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(help_text='Фоловер', on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(limit_value=1, message='Minimum cooking time is 1'), django.core.validators.MaxValueValidator(limit_value=1000, message='Too much time for cooking')], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_in_shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Сборщик продуктовой корзины'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#ff0000', image_field=None, max_length=18, samples=None, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=30, unique=True, verbose_name='Тег'),
        ),
    ]
