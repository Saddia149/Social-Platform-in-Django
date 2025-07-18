# Generated by Django 4.2.7 on 2025-07-13 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='is_resolved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='report',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.post'),
        ),
    ]
