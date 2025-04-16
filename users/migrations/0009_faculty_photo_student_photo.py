# Generated by Django 4.2.10 on 2025-04-08 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_alter_enrollment_student"),
    ]

    operations = [
        migrations.AddField(
            model_name="faculty",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="faculty_photos/"),
        ),
        migrations.AddField(
            model_name="student",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="student_photos/"),
        ),
    ]
