
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('user_answer', models.TextField()),
                ('score', models.IntegerField(blank=True, null=True)),
                ('strengths', models.TextField(blank=True, null=True)),
                ('weaknesses', models.TextField(blank=True, null=True)),
                ('ideal_answer', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('interview', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='interviews.interview')),
            ],
        ),
    ]
