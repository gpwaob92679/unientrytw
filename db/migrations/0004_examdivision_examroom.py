# Generated by Django 4.2.3 on 2023-08-02 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0003_alter_department_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamDivision',
            fields=[
                ('id', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ExamRoom',
            fields=[
                ('id', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db.examdivision')),
            ],
        ),
    ]
