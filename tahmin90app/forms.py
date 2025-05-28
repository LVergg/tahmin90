from django import forms
from .models import Prediction

class PredictionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        if question:
            self.fields['selected_choice'] = forms.ChoiceField(
                choices=[(k, f"{k}) {v}") for k, v in question.choices.items()],
                widget=forms.RadioSelect,
                label=question.text
            )

    class Meta:
        model = Prediction
        fields = ['selected_choice'] 