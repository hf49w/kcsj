# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Person
#from .recommendation_algorithm import run_recommendation_algorithm

@receiver(post_save, sender=Person)
def run_recommendation(sender, instance, **kwargs):
     
    print("run_recommendation_algorithm(instance)")
