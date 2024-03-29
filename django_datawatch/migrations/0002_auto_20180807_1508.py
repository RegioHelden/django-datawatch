# Generated by Django 1.10.2 on 2018-08-07 15:08
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_datawatch', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='assigned_to_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='result',
            name='assigned_to_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_to_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
