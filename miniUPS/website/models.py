from django.db import models

# Do we need add a field which is world_id to differentiate different tests?
# same shipment id but at diff warehouse

# Create your models here.
class User(models.Model):
    name = models.CharField(primary_key = True, max_length=128)
    email = models.EmailField(blank=False, unique=True)
    password = models.CharField(blank=False, max_length=128)
    
class Truck(models.Model):
    status_options = {
        ('idle','idle'),
        ('traveling','traveling'),
        ('arrive warehouse','arrive warehouse'),
        ('loading','loading'),
        ('delivering','delivering')
    }
    truckid = models.AutoField(primary_key = True)
    x = models.IntegerField(blank=False)
    y = models.IntegerField(blank=False)
    status = models.CharField(blank=False, choices=status_options, max_length=128)
    
class Package(models.Model):
    status_options = {
        ('loading','loading'),
        ('loaded','loaded'),
        ('delivering','delivering'),
        ('delivered','delivered')
    }
    tracking_id = models.IntegerField(primary_key = True)
    shipment_id = models.IntegerField(blank=False)
    truckid = models.ForeignKey(to=Truck, verbose_name="FK_truck", 
                                on_delete=models.CASCADE, default=None, blank=False, null=False)
    x = models.IntegerField(blank=False) #destination addr
    y = models.IntegerField(blank=False)
    user = models.ForeignKey(to=User, verbose_name="FK_binded_user", 
                             on_delete=models.SET_NULL, default=None, blank=True, null=True) #user could be null
    status = models.CharField(blank=False, choices=status_options, max_length=128)
    
# record trucks on the way to warehouse(truck status = traveling)
class AssignedTruck(models.Model):
    whid = models.IntegerField(primary_key=True)
    truckid = models.ForeignKey(to=Truck, verbose_name="FK_truck", 
                                on_delete=models.CASCADE, default=None, blank=False, null=False)
    
# handled response from world
# when we receive a response from world, check if the seqnum exists in this table
# ignore (continue) if exist
class WorldRes(models.Model):
    seqnum = models.IntegerField(primary_key=True)
    
# command acked by world
# we constantly send our command in a while loop
# before each repeatative sending we check if our seqnumed command has the matching
# ack num in this table, break loop if exist
class AckedCommand(models.Model):
    seqnum = models.IntegerField(primary_key=True)