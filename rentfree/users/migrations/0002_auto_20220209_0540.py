# Generated by Django 3.2.12 on 2022-02-09 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('djstripe', '0008_2_5'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='stripe_customer',
            field=models.ForeignKey(blank=True, help_text='The user Stripe Customer object, if it exists.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.customer'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stripe_paymentmethod',
            field=models.ForeignKey(blank=True, help_text='The user Stripe Payment Method object, if it exists.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.paymentmethod'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stripe_subscription',
            field=models.ForeignKey(blank=True, help_text='The user Stripe Subscription object, if it exists.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.subscription'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
