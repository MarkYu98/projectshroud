# Generated by Django 2.2.1 on 2019-05-30 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_auto_20190530_0057'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='event',
            name='applicant_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='event',
            name='attendee_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='receive_email',
            field=models.BooleanField(default=True),
        ),
    ]
