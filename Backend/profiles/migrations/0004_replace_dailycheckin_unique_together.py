from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_dailycheckin'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dailycheckin',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='dailycheckin',
            constraint=models.UniqueConstraint(
                fields=('user', 'date'),
                name='unique_daily_checkin_per_user_date',
            ),
        ),
    ]
