# Generated by Django 3.0.5 on 2020-05-07 19:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=64)),
                ('style', models.CharField(max_length=64)),
                ('toppings_qty', models.IntegerField()),
                ('price_small', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, null=True)),
                ('price_large', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('complete', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('S', 'Small'), ('L', 'Large'), (None, 'N/A')], default=None, max_length=1)),
                ('qty', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('menu_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.MenuItem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderItems', to='orders.Order')),
            ],
        ),
        migrations.CreateModel(
            name='SubAddon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Topping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.DeleteModel(
            name='Pizza',
        ),
        migrations.DeleteModel(
            name='SicilianPizza',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='sub_addons',
            field=models.ManyToManyField(related_name='orderAddons', to='orders.SubAddon'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='toppings',
            field=models.ManyToManyField(related_name='orderToppings', to='orders.Topping'),
        ),
    ]
