from django.db import migrations, models
import django.contrib.auth.validators


class Migration(migrations.Migration):
    """
    Reconciles Django's migration state with the current User model definition.

    Django 4.2's AbstractUser ships with a help_text on the username field
    that was not captured in 0001_initial.py.  The autodetector therefore
    sees a mismatch and raises the "Your models in app(s): 'users' have
    changes that are not yet reflected in a migration" error.

    SeparateDatabaseAndState lets us update the recorded migration state
    without issuing any DDL, so the database schema is left untouched while
    Django's internal state tracker is brought back in sync.
    """

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],   # no DDL — schema is already correct
            state_operations=[
                migrations.AlterField(
                    model_name='user',
                    name='username',
                    field=models.CharField(
                        error_messages={'unique': 'A user with that username already exists.'},
                        help_text=(
                            'Required. 150 characters or fewer. '
                            'Letters, digits and @/./+/-/_ only.'
                        ),
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name='username',
                    ),
                ),
                migrations.AlterField(
                    model_name='user',
                    name='first_name',
                    field=models.CharField(
                        blank=True,
                        max_length=150,
                        verbose_name='first name',
                    ),
                ),
            ],
        ),
    ]
