from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

DEFAULT_QUESTIONS = [
    {
        "text": "Maçı kim kazanır?",
        "choices": {
            "A": "Ev sahibi",
            "B": "Beraberlik",
            "C": "Deplasman"
        }
    },
    {
        "text": "Hangi yarıda daha fazla gol olur?",
        "choices": {
            "A": "1. Yarı",
            "B": "Eşit",
            "C": "2. Yarı",
            "D": "Gol olmaz"
        }
    },
    {
        "text": "İlk kartı hangi takım görür?",
        "choices": {
            "A": "Ev sahibi",
            "B": "Beraberlik",
            "C": "Deplasman"
        }
    },
    {
        "text": "Toplam köşe vuruşu sayısı kaç olur?",
        "choices": {
            "A": "0-5 Arası",
            "B": "6-10 Arası",
            "C": "11 ve üzeri"
        }
    },
    {
        "text": "Kaleyi bulan toplam isabetli şut sayısı kaç olur?",
        "choices": {
            "A": "0-5 Arası",
            "B": "6-10 Arası",
            "C": "11 ve üzeri"
        }
    }
]

class MatchEvent(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(
        help_text="Maçın başlangıç zamanı",
        default=timezone.now
    )

    def clean(self):
        if not self.pk and MatchEvent.objects.exists():
            raise ValidationError("Sadece bir aktif maç olabilir. Yeni bir maç eklemeden önce mevcut maçı silin.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active_match(cls):
        return cls.objects.first()

    def get_statistics(self):
        total_predictions = self.predictiongroup_set.count()
        rewarded_count = self.predictiongroup_set.filter(reward_granted=True).count()
        rewarded_percentage = (rewarded_count / total_predictions * 100) if total_predictions > 0 else 0

        question_stats = {}
        for question in self.questions.all():
            correct_count = question.prediction_set.filter(is_correct=True).count()
            total_count = question.prediction_set.count()
            percentage = (correct_count / total_count * 100) if total_count > 0 else 0
            
            question_stats[question.text] = {
                'total': total_count,
                'correct': correct_count,
                'percentage': round(percentage, 2)
            }

        return {
            'total_predictions': total_predictions,
            'rewarded_count': rewarded_count,
            'rewarded_percentage': round(rewarded_percentage, 2),
            'question_stats': question_stats
        }

    def __str__(self):
        return self.title


class Question(models.Model):
    match = models.ForeignKey(MatchEvent, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=255)
    choices = models.JSONField()
    correct_answer = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return f"{self.match.title} | {self.text}"


class PredictionGroup(models.Model):
    user = models.CharField(max_length=100)
    user_code = models.CharField(max_length=50, default='anonymous')
    email = models.EmailField(default='anonymous@example.com')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    match = models.ForeignKey(MatchEvent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reward_granted = models.BooleanField(default=False, help_text="Ödül verildi mi?")
    
    def __str__(self):
        return f"[{self.user_code}] {self.user}'s predictions for {self.match.title}"


class Prediction(models.Model):
    match = models.ForeignKey(MatchEvent, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.CharField(max_length=100, default="anonymous")
    selected_choice = models.CharField(max_length=1, default='A')
    is_correct = models.BooleanField(default=False)
    group = models.ForeignKey(PredictionGroup, on_delete=models.CASCADE, related_name='predictions', null=True)

    def __str__(self):
        return f"{self.user} - {self.question.text} -> {self.selected_choice}"
