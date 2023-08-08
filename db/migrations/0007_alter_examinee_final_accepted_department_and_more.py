# Generated by Django 4.2.3 on 2023-08-08 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0006_examinee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examinee',
            name='final_accepted_department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='final_accepted_examinees', to='db.department'),
        ),
        migrations.AlterField(
            model_name='examinee',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]