# users/migrations/0002_auto_fix_user_state.py
from django.db import migrations, models
import django.contrib.auth.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='user',
                    name='username',
                    field=models.CharField(
                        error_messages={'unique': 'A user with that username already exists.'},
                        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
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
            database_operations=[],  # DDL не выполняем — схема уже правильная
        ),
    ]