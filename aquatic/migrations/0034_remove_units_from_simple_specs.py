from django.db import migrations


def remove_spec_units(apps, schema_editor):
    AquaticLife = apps.get_model("aquatic", "AquaticLife")

    for item in AquaticLife.objects.all():
        update_fields = []

        # 例如：
        # 24～28°C → 24～28
        # 24°C 以上 → 24 以上
        # 28°C 以下 → 28 以下
        if item.temp:
            cleaned_temp = item.temp.replace("°C", "").replace("℃", "").strip()

            if cleaned_temp != item.temp:
                item.temp = cleaned_temp
                update_fields.append("temp")

        # 例如：
        # 成魚約 5 cm → 成魚約 5
        # 3～5cm → 3～5
        # 約 3 公分 → 約 3
        if item.body_length:
            cleaned_length = (
                item.body_length.replace("cm", "")
                .replace("CM", "")
                .replace("公分", "")
                .replace("厘米", "")
                .strip()
            )

            # 清除移除單位後可能留下的多餘空格
            cleaned_length = " ".join(cleaned_length.split())

            if cleaned_length != item.body_length:
                item.body_length = cleaned_length
                update_fields.append("body_length")

        if update_fields:
            item.save(update_fields=update_fields)


def reverse_remove_spec_units(apps, schema_editor):
    # 無法判斷舊資料原本使用 °C、℃、cm 或公分，
    # 因此不自動加回單位。
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "aquatic",
            "0033_migrate_simple_specs",
        ),
    ]

    operations = [
        migrations.RunPython(
            remove_spec_units,
            reverse_remove_spec_units,
        ),
    ]
