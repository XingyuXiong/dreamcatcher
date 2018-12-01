# Generated by Django 2.1.3 on 2018-12-01 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('honor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Angel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_name', models.CharField(max_length=30)),
                ('registered_id', models.CharField(max_length=30)),
                ('identifier', models.CharField(max_length=100)),
                ('nickname', models.CharField(max_length=30)),
                ('phone', models.CharField(max_length=15)),
                ('avatar', models.ImageField(upload_to='')),
                ('contribution', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('avatar', models.ImageField(upload_to='')),
                ('description', models.TextField()),
                ('honors', models.ManyToManyField(to='honor.Honor')),
                ('leader', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='led_group', to='angel.Angel')),
            ],
        ),
        migrations.AddField(
            model_name='angel',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='angels', to='angel.Group'),
        ),
        migrations.AddField(
            model_name='angel',
            name='honors',
            field=models.ManyToManyField(to='honor.Honor'),
        ),
    ]