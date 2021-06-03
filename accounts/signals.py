from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import Customer

def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name = 'customer') # here the customer will automatically added up in customer group
        instance.groups.add(group) 
        Customer.objects.create(
            user = instance,
            name = instance.username,
        )  #Added username because of error returning customer
         # with this new customer will automatically shift to status.html page after login 
                                                    #and can see its order status
        print('Profile Created')                                            
post_save.connect(customer_profile, sender = User)        