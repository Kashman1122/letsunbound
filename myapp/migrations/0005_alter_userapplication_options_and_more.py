# Generated by Django 5.1.7 on 2025-03-28 08:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_college_userapplication'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userapplication',
            options={'ordering': ['-application_date'], 'verbose_name': 'University Application', 'verbose_name_plural': 'University Applications'},
        ),
        migrations.AlterField(
            model_name='userapplication',
            name='college',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicant_set', to='myapp.college'),
        ),
        migrations.AlterField(
            model_name='userapplication',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Additional Notes'),
        ),
        migrations.AlterField(
            model_name='userapplication',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='university_applications', to=settings.AUTH_USER_MODEL),
        ),
    ]
