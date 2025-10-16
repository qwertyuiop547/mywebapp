import json
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.contrib.admin.views.decorators import staff_member_required
from .models import ChatSession, ChatMessage, ChatbotKnowledgeBase, ChatbotAnalytics, ProactiveAlert, ChatImageUpload
from .ai_engine import BarangayAIEngine
from .api_services import weather_service, translation_service
import os
from PIL import Image


@require_http_methods(["POST"])
def chat_api(request):
    """Main chat API endpoint"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        language = data.get('language', 'en')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create session
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                pass
        
        if not session:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                language=language
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Get user context for better responses
        user_context = {}
        if request.user.is_authenticated:
            user_context = {
                'role': getattr(request.user, 'role', 'resident'),
                'is_verified': getattr(request.user, 'is_verified', False),
                'username': request.user.username
            }
        
        # Generate AI response with session context
        ai_engine = BarangayAIEngine()
        ai_response = ai_engine.process_message(
            message=message, 
            language=language, 
            user_context=user_context,
            session_id=session.session_id  # Pass session_id for context tracking
        )
        
        # Update session language if detected language is different
        detected_lang = ai_response.get('detected_language', language)
        if detected_lang and detected_lang != session.language:
            session.language = detected_lang
            session.save()
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=ai_response['response']
        )
        
        # Update session language if different
        if session.language != language:
            session.language = language
            session.save()
        
        response_data = {
            'session_id': session.session_id,
            'response': ai_response['response'],
            'confidence': ai_response['confidence'],
            'category': ai_response['category'],
            'suggestions': ai_response.get('suggestions', []),
            'message_id': bot_message.id,
            'timestamp': bot_message.timestamp.isoformat()
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["POST"])
def start_session(request):
    """Start a new chat session"""
    try:
        data = json.loads(request.body)
        language = data.get('language', 'en')
        
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id,
            language=language
        )
        
        # Create welcome message
        ai_engine = BarangayAIEngine()
        welcome_response = ai_engine.process_message('hello', language)
        
        ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=welcome_response['response']
        )
        
        return JsonResponse({
            'session_id': session.session_id,
            'welcome_message': welcome_response['response'],
            'suggestions': welcome_response.get('suggestions', [])
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["POST"])
def end_session(request):
    """End a chat session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)
        
        try:
            session = ChatSession.objects.get(session_id=session_id, is_active=True)
            session.is_active = False
            session.ended_at = timezone.now()
            session.save()
            
            return JsonResponse({'success': True})
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["POST"])
def submit_feedback(request):
    """Submit feedback for a chat message"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        is_helpful = data.get('is_helpful')
        
        if not message_id or is_helpful is None:
            return JsonResponse({'error': 'Message ID and feedback are required'}, status=400)
        
        try:
            message = ChatMessage.objects.get(id=message_id, message_type='bot')
            message.is_helpful = is_helpful
            message.save()
            
            return JsonResponse({'success': True})
        except ChatMessage.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)


@staff_member_required
def knowledge_base_admin(request):
    """Admin view for managing knowledge base"""
    knowledge_items = ChatbotKnowledgeBase.objects.all().order_by('-priority', 'category')
    
    # Get analytics
    today = timezone.now().date()
    analytics = ChatbotAnalytics.objects.filter(date=today).first()
    
    context = {
        'knowledge_items': knowledge_items,
        'analytics': analytics,
        'categories': ChatbotKnowledgeBase.CATEGORY_CHOICES,
    }
    
    return render(request, 'chatbot/knowledge_base_admin.html', context)


@require_http_methods(["POST"])
def upload_image_api(request):
    """Handle image upload and analysis"""
    try:
        image_file = request.FILES.get('image')
        session_id = request.POST.get('session_id')
        language = request.POST.get('language', 'en')
        
        if not image_file:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        # Get or create session
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                pass
        
        if not session:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                language=language
            )
        
        # Save uploaded image
        chat_image = ChatImageUpload.objects.create(
            session=session,
            image=image_file,
            original_filename=image_file.name
        )
        
        # Simple image analysis (you can enhance this with actual AI)
        ai_analysis = analyze_image(image_file, language)
        chat_image.ai_analysis = ai_analysis
        chat_image.save()
        
        # Generate appropriate response
        response_text = generate_image_response(ai_analysis, language)
        
        # Save bot response
        ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=response_text
        )
        
        return JsonResponse({
            'session_id': session.session_id,
            'response': response_text,
            'suggestions': get_image_suggestions(language),
            'analysis': ai_analysis
        })
        
    except Exception as e:
        return JsonResponse({'error': 'Image processing failed'}, status=500)


@require_http_methods(["GET"])
def get_alerts_api(request):
    """Get active proactive alerts"""
    try:
        current_time = timezone.now()
        
        # Get active, non-expired alerts
        alerts_query = ProactiveAlert.objects.filter(
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=current_time)
        )
        
        # Filter by language if specified
        language = request.GET.get('language', 'en')
        alerts_query = alerts_query.filter(
            Q(target_language='both') | Q(target_language=language)
        ).order_by('-priority', '-created_at')[:5]  # Limit to 5 most important alerts
        
        alerts_data = []
        for alert in alerts_query:
            alerts_data.append({
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'type': alert.alert_type,
                'priority': alert.priority,
                'created_at': alert.created_at.isoformat()
            })
        
        return JsonResponse({'alerts': alerts_data})
        
    except Exception as e:
        return JsonResponse({'error': 'Failed to get alerts'}, status=500)


def analyze_image(image_file, language='en'):
    """Simple image analysis - can be enhanced with actual AI services"""
    try:
        # Basic image info
        with Image.open(image_file) as img:
            width, height = img.size
            format = img.format
            mode = img.mode
        
        # Simple analysis based on filename and properties
        filename = image_file.name.lower()
        
        if any(word in filename for word in ['damage', 'broken', 'problem', 'issue']):
            return "The image appears to show some kind of damage or issue that may need barangay attention."
        elif any(word in filename for word in ['document', 'paper', 'id', 'certificate']):
            return "This appears to be a document or identification paper."
        elif any(word in filename for word in ['road', 'street', 'pathway']):
            return "This image shows a road or pathway in the barangay."
        else:
            return f"Image received: {filename} ({width}x{height} pixels, {format} format)"
            
    except Exception as e:
        return "Image analysis could not be completed."


def generate_image_response(analysis, language='en'):
    """Generate appropriate response based on image analysis"""
    responses = {
        'en': {
            'damage': "I can see there might be an issue in the image. Would you like to file a complaint about this? I can help guide you through the process.",
            'document': "I see you've uploaded a document. Are you looking for help with document verification or do you need information about barangay certificates?",
            'road': "This appears to be about road or infrastructure. If there are any issues, I can help you report them to the appropriate barangay officials.",
            'general': "Thanks for sharing the image. How can I help you with this? You can ask me about filing complaints, getting services, or any barangay-related questions."
        },
        'fil': {
            'damage': "Nakikita ko na may issue sa larawan. Gusto mo bang mag-file ng reklamo tungkol dito? Matutulungan kita sa proseso.",
            'document': "Nakita ko na nag-upload ka ng dokumento. Tumutulong ka ba sa document verification o kailangan mo ng impormasyon tungkol sa barangay certificates?",
            'road': "Mukhang tungkol ito sa daan o infrastructure. Kung may mga issue, matutulungan kita na i-report sa tamang barangay officials.",
            'general': "Salamat sa pag-share ng larawan. Paano kita matutulungan? Pwede mo akong tanungin tungkol sa pag-file ng reklamo, pagkuha ng serbisyo, o anumang barangay-related na tanong."
        }
    }
    
    lang_responses = responses.get(language, responses['en'])
    
    if 'damage' in analysis.lower() or 'issue' in analysis.lower():
        return lang_responses['damage']
    elif 'document' in analysis.lower() or 'paper' in analysis.lower():
        return lang_responses['document']
    elif 'road' in analysis.lower() or 'pathway' in analysis.lower():
        return lang_responses['road']
    else:
        return lang_responses['general']


def get_image_suggestions(language='en'):
    """Get suggestions after image upload"""
    suggestions = {
        'en': [
            "File a complaint about this issue",
            "Get document verification help",
            "Report infrastructure problem",
            "Ask about barangay services"
        ],
        'fil': [
            "Mag-file ng reklamo tungkol dito",
            "Kumuha ng tulong sa dokumento",
            "I-report ang problema sa infrastructure",
            "Magtanong tungkol sa serbisyo"
        ]
    }
    
    return suggestions.get(language, suggestions['en'])
