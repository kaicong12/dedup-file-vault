# Generated by Django 4.2.23 on 2025-07-07 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_hash',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['file_hash'], name='files_file_file_ha_868749_idx'),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['size', 'file_hash'], name='files_file_size_128caf_idx'),
        ),
    ]
