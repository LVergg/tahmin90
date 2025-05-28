from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MatchEvent, Question, DEFAULT_QUESTIONS

@receiver(post_save, sender=MatchEvent)
def create_default_questions(sender, instance, created, **kwargs):
    if created:
        for q in DEFAULT_QUESTIONS:
            Question.objects.create(
                match=instance,
                text=q["text"],
                choices=q["choices"]
            ) 