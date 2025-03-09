# Generated by Django 5.1.5 on 2025-02-06 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_alter_course_remainingcapacity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='remainingCapacity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='nationalID',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='studentNumber',
            field=models.CharField(max_length=9, unique=True),
        ),
    ]
