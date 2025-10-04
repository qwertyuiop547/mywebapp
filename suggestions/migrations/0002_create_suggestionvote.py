from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('suggestions', '0001_initial'),
    ]

    operations = [
        # Create only the SuggestionVote table (for DBs where initial was faked)
        migrations.CreateModel(
            name='SuggestionVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('suggestion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='suggestions.suggestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Suggestion Vote',
                'verbose_name_plural': 'Suggestion Votes',
                'unique_together': {('suggestion', 'user')},
            },
        ),
    ]


