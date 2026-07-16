from django.db import migrations


def copy_old_specs(apps, schema_editor):
    AquaticLife = apps.get_model("aquatic", "AquaticLife")

    for item in AquaticLife.objects.all():
        update_fields = []

        # 舊的最低與最高溫度，轉成新版文字欄位
        if not item.temp:
            if item.temp_min is not None and item.temp_max is not None:
                item.temp = f"{item.temp_min}～{item.temp_max}°C"
                update_fields.append("temp")

            elif item.temp_min is not None:
                item.temp = f"{item.temp_min}°C 以上"
                update_fields.append("temp")

            elif item.temp_max is not None:
                item.temp = f"{item.temp_max}°C 以下"
                update_fields.append("temp")

        # 舊成魚體長，轉成新版文字欄位
        if not item.body_length and item.adult_length is not None:
            item.body_length = f"成魚約 {item.adult_length:g} cm"
            update_fields.append("body_length")

        if update_fields:
            item.save(update_fields=update_fields)


def reverse_copy(apps, schema_editor):
    # 新欄位是自由文字，無法可靠拆回舊的數字欄位
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "aquatic",
            "0032_aquaticlife_body_length_aquaticlife_temp",
        ),
    ]

    operations = [
        migrations.RunPython(
            copy_old_specs,
            reverse_copy,
        ),
    ]
