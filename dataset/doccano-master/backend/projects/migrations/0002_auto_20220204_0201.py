# Generated by Django 3.2.11 on 2022-02-04 02:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Project",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                            ),
                        ),
                        ("name", models.CharField(max_length=100)),
                        ("description", models.TextField(default="")),
                        ("guideline", models.TextField(blank=True, default="")),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        (
                            "project_type",
                            models.CharField(
                                choices=[
                                    ("DocumentClassification", "document classification"),
                                    ("SequenceLabeling", "sequence labeling"),
                                    ("Seq2seq", "sequence to sequence"),
                                    ("IntentDetectionAndSlotFilling", "intent detection and slot filling"),
                                    ("Speech2text", "speech to text"),
                                    ("ImageClassification", "image classification"),
                                ],
                                max_length=30,
                            ),
                        ),
                        ("random_order", models.BooleanField(default=False)),
                        ("collaborative_annotation", models.BooleanField(default=False)),
                        ("single_class_classification", models.BooleanField(default=False)),
                        (
                            "created_by",
                            models.ForeignKey(
                                null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                            ),
                        ),
                        (
                            "polymorphic_ctype",
                            models.ForeignKey(
                                editable=False,
                                null=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="polymorphic_projects.project_set+",
                                to="contenttypes.contenttype",
                            ),
                        ),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                ),
                migrations.CreateModel(
                    name="ImageClassificationProject",
                    fields=[
                        (
                            "project_ptr",
                            models.OneToOneField(
                                auto_created=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                parent_link=True,
                                primary_key=True,
                                serialize=False,
                                to="projects.project",
                            ),
                        ),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                    bases=("projects.project",),
                ),
                migrations.CreateModel(
                    name="IntentDetectionAndSlotFillingProject",
                    fields=[
                        (
                            "project_ptr",
                            models.OneToOneField(
                                auto_created=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                parent_link=True,
                                primary_key=True,
                                serialize=False,
                                to="projects.project",
                            ),
                        ),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                    bases=("projects.project",),
                ),
                migrations.CreateModel(
                    name="Seq2seqProject",
                    fields=[
                        (
                            "project_ptr",
                            models.OneToOneField(
                                auto_created=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                parent_link=True,
                                primary_key=True,
                                serialize=False,
                                to="projects.project",
                            ),
                        ),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                    bases=("projects.project",),
                ),
                migrations.CreateModel(
                    name="SequenceLabelingProject",
                    fields=[
                        (
                            "project_ptr",
                            models.OneToOneField(
                                auto_created=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                parent_link=True,
                                primary_key=True,
                                serialize=False,
                                to="projects.project",
                            ),
                        ),
                        ("allow_overlapping", models.BooleanField(default=False)),
                        ("grapheme_mode", models.BooleanField(default=False)),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                    bases=("projects.project",),
                ),
                migrations.CreateModel(
                    name="Speech2textProject",
                    fields=[
                        (
                            "project_ptr",
                            models.OneToOneField(
                                auto_created=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                parent_link=True,
                                primary_key=True,
                                serialize=False,
                                to="projects.project",
                            ),
                        ),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                    bases=("projects.project",),
                ),
                migrations.CreateModel(
                    name="TextClassificationProject",
                    fields=[
                        (
                            "project_ptr",
                            models.OneToOneField(
                                auto_created=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                parent_link=True,
                                primary_key=True,
                                serialize=False,
                                to="projects.project",
                            ),
                        ),
                    ],
                    options={
                        "abstract": False,
                        "base_manager_name": "objects",
                    },
                    bases=("projects.project",),
                ),
                migrations.CreateModel(
                    name="Tag",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                            ),
                        ),
                        ("text", models.TextField()),
                        (
                            "project",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE, related_name="tags", to="projects.project"
                            ),
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name="member",
                    name="project",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="role_mappings", to="projects.project"
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    UPDATE django_content_type
                    SET app_label = 'projects'
                    WHERE app_label = 'api' AND model LIKE '%project'
                    """,
                    reverse_sql="""
                    UPDATE django_content_type
                    SET app_label = 'api'
                    WHERE app_label = 'projects' AND model LIKE '%project'
                    """,
                )
            ],
        )
    ]
