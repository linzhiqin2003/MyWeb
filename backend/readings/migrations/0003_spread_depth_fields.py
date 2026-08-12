from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("readings", "0002_spread_reading_spread"),
    ]

    operations = [
        migrations.AddField(
            model_name="spread",
            name="allow_reversed",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="spread",
            name="blurb",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="spread",
            name="category",
            field=models.CharField(
                choices=[
                    ("glance", "速览"),
                    ("classic", "经典"),
                    ("depth", "深度"),
                    ("relation", "关系"),
                    ("decision", "抉择"),
                    ("inner", "内在"),
                    ("timing", "时序"),
                ],
                default="classic",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="spread",
            name="description_cn",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="spread",
            name="difficulty",
            field=models.CharField(
                choices=[
                    ("beginner", "入门"),
                    ("intermediate", "进阶"),
                    ("advanced", "高阶"),
                ],
                default="beginner",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="spread",
            name="positions_cn",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="spread",
            name="sort_order",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="spread",
            options={"ordering": ["sort_order", "card_count", "id"]},
        ),
        migrations.AddField(
            model_name="reading",
            name="ai_advice",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="reading",
            name="ai_summary",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="reading",
            name="mode",
            field=models.CharField(default="ritual", max_length=20),
        ),
        migrations.AddField(
            model_name="reading",
            name="tone",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
        migrations.AddField(
            model_name="reading",
            name="verdict",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
