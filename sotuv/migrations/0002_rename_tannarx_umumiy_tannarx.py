from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sotuv', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mahsulotpartiyasi',
            old_name='tannarx',
            new_name='umumiy_tannarx',
        ),
        migrations.AlterField(
            model_name='mahsulotpartiyasi',
            name='umumiy_tannarx',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12, null=True,
                help_text="Butun partiya uchun umumiy tannarx (masalan 2100 dona uchun jami qancha to'langan bo'lsa)",
            ),
        ),
    ]
