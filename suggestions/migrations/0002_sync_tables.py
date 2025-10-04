# Safe migration to sync existing tables with Django's migration state
from django.db import migrations


def sync_existing_tables(apps, schema_editor):
    """
    This migration does nothing - it just marks the migration as applied.
    Use this when tables already exist in the database.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('suggestions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_existing_tables, reverse_code=migrations.RunPython.noop),
    ]

