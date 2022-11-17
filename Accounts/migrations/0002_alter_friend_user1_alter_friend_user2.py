# Generated by Django 4.0 on 2022-01-04 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user11', to='Accounts.useraccount'),
        ),
        migrations.AlterField(
            model_name='friend',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user22', to='Accounts.useraccount'),
        ),
    ]
