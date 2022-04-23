# Generated by Django 4.0.4 on 2022-04-23 02:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AckedCommand',
            fields=[
                ('seqnum', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('truckid', models.AutoField(primary_key=True, serialize=False)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('status', models.CharField(choices=[('LOADING', 'loading'), ('DELIVERING', 'delivering'), ('ARRIVE WAREHOUSE', 'arrive warehouse'), ('IDLE', 'idle'), ('TRAVELING', 'traveling')], max_length=128)),
                ('pac_num', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('username', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='WorldRes',
            fields=[
                ('seqnum', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('tracking_id', models.AutoField(primary_key=True, serialize=False)),
                ('shipment_id', models.IntegerField(unique=True)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('status', models.CharField(choices=[('loaded', 'loaded'), ('in WH', 'in WH'), ('delivered', 'delivered'), ('loading', 'loading'), ('delivering', 'delivering')], max_length=128)),
                ('truckid', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='website.truck', verbose_name='FK_truck')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.user', verbose_name='FK_binded_user')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=128)),
                ('count', models.IntegerField()),
                ('tracking_id', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='website.package', verbose_name='FK_Package')),
            ],
        ),
        migrations.CreateModel(
            name='AssignedTruck',
            fields=[
                ('count', models.AutoField(primary_key=True, serialize=False)),
                ('whid', models.IntegerField()),
                ('truckid', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='website.truck', verbose_name='FK_truck')),
            ],
        ),
    ]
