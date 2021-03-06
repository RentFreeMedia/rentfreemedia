# Generated by Django 3.2.12 on 2022-02-28 00:38

from django.db import migrations, models
import post_office.validators


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_alter_custommedia_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalsettings',
            name='from_email',
            field=models.CharField(default='contact@dubiouspod.com', help_text='The default email address this site sends from, may include name, ex: "Admin <admin@admin.com>"', max_length=255, validators=[post_office.validators.validate_email_with_name], verbose_name='From email'),
        ),
    ]
