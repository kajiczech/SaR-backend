# Generated by Django 2.1.7 on 2019-07-28 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190728_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(blank=True, null=True, related_name='users', to='core.Role'),
        ),
    ]
