from django.db import migrations


class Migration(migrations.Migration):
    """
    Empty migration to reconcile Django's migration state with the current
    model definition. This resolves the "Your models in app(s): 'users' have
    changes that are not yet reflected in a migration" error without altering
    any database schema.
    """

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = []
