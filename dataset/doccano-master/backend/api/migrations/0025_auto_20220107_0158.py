# Generated by Django 3.2.8 on 2022-01-07 01:58

from django.db import migrations


def recover_label(apps, schema_editor):
    CategoryType = apps.get_model("api", "CategoryType")
    SpanType = apps.get_model("api", "SpanType")
    Label = apps.get_model("api", "Label")
    for model in [CategoryType, SpanType]:
        for label in model.objects.all():
            old_label = Label(
                id=label.id,
                text=label.text,
                prefix_key=label.prefix_key,
                suffix_key=label.suffix_key,
                project=label.project,
                background_color=label.background_color,
                text_color=label.text_color,
                created_at=label.created_at,
                updated_at=label.updated_at,
            )
            old_label.save()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0024_auto_20211221_1444"),
    ]

    operations = [migrations.RunPython(code=migrations.RunPython.noop, reverse_code=recover_label)]
