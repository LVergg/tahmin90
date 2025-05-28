from django.contrib import admin
from django.http import HttpResponse
from datetime import datetime
import csv
from .models import MatchEvent, Question, Prediction, PredictionGroup

@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('match', 'text', 'correct_answer')
    readonly_fields = ('choices',)
    search_fields = ('text',)
    list_filter = ('match',)

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'question', 'selected_choice', 'is_correct')
    search_fields = ('user',)
    list_filter = ('match', 'question', 'is_correct')

@admin.register(PredictionGroup)
class PredictionGroupAdmin(admin.ModelAdmin):
    list_display = ('match', 'user_code', 'user', 'email', 'phone_number', 'created_at', 'reward_granted')
    search_fields = ('user_code', 'user', 'email', 'phone_number')
    list_filter = ('match', 'created_at', 'reward_granted')
    list_editable = ('reward_granted',)
    actions = ['mark_rewards_granted', 'mark_rewards_not_granted', 'export_as_csv']

    def mark_rewards_granted(self, request, queryset):
        queryset.update(reward_granted=True)
    mark_rewards_granted.short_description = "Seçili tahminlerin ödüllerini verildi olarak işaretle"

    def mark_rewards_not_granted(self, request, queryset):
        queryset.update(reward_granted=False)
    mark_rewards_not_granted.short_description = "Seçili tahminlerin ödüllerini verilmedi olarak işaretle"

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ['match', 'user_code', 'user', 'email', 'phone_number', 'created_at', 'reward_granted']
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=prediction_groups_{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        # BOM karakteri ekleyerek Excel'in UTF-8'i doğru tanımasını sağlıyoruz
        response.write('\ufeff'.encode('utf-8'))
        
        writer = csv.writer(response, lineterminator='\n')
        writer.writerow(field_names)
        
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if field == 'match':
                    value = str(value)
                elif field == 'created_at':
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row.append(value)
            writer.writerow(row)
        
        return response
    
    export_as_csv.short_description = "Seçili tahminleri CSV olarak dışa aktar"
