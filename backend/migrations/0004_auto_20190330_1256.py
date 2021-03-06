# Generated by Django 2.1.7 on 2019-03-30 04:56

import backend.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_auto_20190330_0333'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckIn',
            fields=[
                ('token', models.CharField(default=backend.models.generate_user_uuid, editable=False, max_length=16, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='checkin_enabled',
            field=models.BooleanField(default=False, verbose_name='正在签到'),
        ),
        migrations.AlterUniqueTogether(
            name='usermanageevent',
            unique_together={('user', 'event')},
        ),
        migrations.AlterUniqueTogether(
            name='userregisterevent',
            unique_together={('user', 'event')},
        ),
        migrations.AddField(
            model_name='checkin',
            name='event',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.Event'),
        ),
    ]
