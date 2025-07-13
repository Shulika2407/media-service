from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


# @receiver(pre_delete, sender=Question)
# def delete_user_profile(sender, instance, **kwargs):
#     delete_profile = Deleted()
#     delete_profile.question = instance.id
#     delete_profile.dt = datetime.datetime.now()
#     delete_profile.save()
