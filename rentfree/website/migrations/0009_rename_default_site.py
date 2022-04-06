from django.db import migrations
import os


def setup_default_site(apps, schema_editor):
    """
    Set up or rename the default example.com site created by Django.
    """
    Site = apps.get_model("sites", "Site")

    name = os.environ.get('DOBASE_URL')
    domain = os.environ.get('DOSITE_NAME')

    try:
        site = Site.objects.get(domain="example.com")
        site.name = name
        site.domain = domain
        site.save()

    except Site.DoesNotExist:
        # No site with domain example.com exists.
        # Create a default site, but only if no sites exist.
        if Site.objects.count() == 0:
            Site.objects.create(name=name, domain=domain)


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0008_alter_generalsettings_from_email"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(setup_default_site, migrations.RunPython.noop),
    ]
