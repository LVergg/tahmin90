from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Question, Prediction, MatchEvent, PredictionGroup
from .forms import PredictionForm

# Create your views here.

def match_questions(request, match_id):
    match = get_object_or_404(MatchEvent, id=match_id)
    questions = match.questions.all()
    
    # Kullanıcının bu maç için daha önce tahmin yapıp yapmadığını kontrol et
    user = request.user.username if request.user.is_authenticated else "anonim"
    existing_group = PredictionGroup.objects.filter(user=user, match=match).first()
    
    if existing_group:
        messages.warning(request, "Bu maç için zaten tahminlerinizi gönderdiniz!")
        return redirect('match_detail', match_id=match_id)  # Bu view'ı daha sonra oluşturacağız
    
    if request.method == 'POST':
        # Tüm sorular cevaplanmış mı kontrol et
        answered_questions = [key for key in request.POST.keys() if key.startswith('question_')]
        if len(answered_questions) != questions.count():
            messages.error(request, "Lütfen tüm soruları cevaplayın!")
            return render(request, 'tahmin90app/match_questions.html', {'match': match, 'questions': questions})
        
        # Yeni bir tahmin grubu oluştur
        prediction_group = PredictionGroup.objects.create(
            user=user,
            match=match
        )
        
        # Her soru için tahmin oluştur
        for question in questions:
            selected_choice = request.POST.get(f'question_{question.id}')
            if selected_choice:
                Prediction.objects.create(
                    match=match,
                    question=question,
                    user=user,
                    selected_choice=selected_choice,
                    group=prediction_group
                )
        
        messages.success(request, "Tahminleriniz başarıyla kaydedildi!")
        return redirect('thanks')
    
    return render(request, 'tahmin90app/match_questions.html', {'match': match, 'questions': questions})

def check_existing_prediction(match, user_code, email, phone_number=None):
    """
    Verilen maç için aynı kullanıcı kodu, email veya telefon numarası ile
    daha önce tahmin yapılıp yapılmadığını kontrol eder.
    """
    query = Q(match=match) & (
        Q(user_code=user_code) |
        Q(email=email)
    )
    
    if phone_number:
        query |= Q(match=match, phone_number=phone_number)
    
    existing = PredictionGroup.objects.filter(query).first()
    
    if existing:
        if existing.user_code == user_code:
            return "Bu kullanıcı kodu"
        elif existing.email == email:
            return "Bu email adresi"
        elif phone_number and existing.phone_number == phone_number:
            return "Bu telefon numarası"
    
    return None

def submit_predictions(request, match_id):
    match = get_object_or_404(MatchEvent, id=match_id)
    questions = match.questions.all()
    
    # Maç başlangıç zamanı kontrolü
    if timezone.now() > match.start_time - timedelta(minutes=5):
        return render(request, 'tahmin90app/prediction_closed.html', {
            'match': match,
            'message': "Tahmin süresi dolmuştur."
        })
    
    context = {
        'match': match,
        'questions': questions,
        'field_errors': {},
        'remaining_time': match.start_time - timezone.now()
    }
    
    if request.method == 'POST':
        # Kullanıcı bilgilerini al
        user_code = request.POST.get('user_code')
        username = request.POST.get('username', 'anonim')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number', '').strip() or None
        
        # Gerekli alanların dolu olduğunu kontrol et
        if not all([user_code, email]):
            messages.error(request, "Kullanıcı kodu ve email adresi zorunludur!")
            return render(request, 'tahmin90app/prediction_form.html', context)
        
        # Mevcut tahmin kontrolü
        existing_type = check_existing_prediction(match, user_code, email, phone_number)
        if existing_type:
            context['field_errors'] = {
                'general': f"{existing_type} ile bu maç için zaten tahmin gönderilmiş!"
            }
            return render(request, 'tahmin90app/prediction_form.html', context)
        
        try:
            # Yeni bir tahmin grubu oluştur
            prediction_group = PredictionGroup.objects.create(
                user=username,
                user_code=user_code,
                email=email,
                phone_number=phone_number,
                match=match
            )
            
            # Her soru için tahmin oluştur
            for question in questions:
                selected_choice = request.POST.get(f'question_{question.id}')
                if selected_choice:
                    Prediction.objects.create(
                        match=match,
                        question=question,
                        user=username,
                        selected_choice=selected_choice,
                        group=prediction_group
                    )
            
            messages.success(request, "Tahminleriniz başarıyla kaydedildi!")
            return redirect('thanks')
            
        except Exception as e:
            messages.error(request, "Tahminleriniz kaydedilirken bir hata oluştu. Lütfen tekrar deneyin.")
            return render(request, 'tahmin90app/prediction_form.html', context)
    
    return render(request, 'tahmin90app/prediction_form.html', context)

def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = request.user.username if request.user.is_authenticated else "anonim"
    
    # Kullanıcının bu maç için daha önce tahmin yapıp yapmadığını kontrol et
    existing_group = PredictionGroup.objects.filter(user=user, match=question.match).first()
    if existing_group:
        messages.warning(request, "Bu maç için zaten tahminlerinizi gönderdiniz!")
        return redirect('match_detail', match_id=question.match.id)

    if request.method == 'POST':
        form = PredictionForm(request.POST, question=question)
        if form.is_valid():
            # Yeni bir tahmin grubu oluştur
            prediction_group = PredictionGroup.objects.create(
                user=user,
                match=question.match
            )
            
            prediction = form.save(commit=False)
            prediction.question = question
            prediction.match = question.match
            prediction.user = user
            prediction.group = prediction_group
            prediction.save()
            
            messages.success(request, "Tahmininiz başarıyla kaydedildi!")
            return redirect('thanks')
    else:
        form = PredictionForm(question=question)

    return render(request, 'tahmin90app/answer_question.html', {'form': form, 'question': question})

def thanks(request):
    return render(request, 'tahmin90app/thanks.html')
