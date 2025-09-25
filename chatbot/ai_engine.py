import re
import random
from typing import Dict, List, Tuple
from django.utils import timezone
from .models import ChatbotKnowledgeBase
from .api_services import smart_response_service, weather_service, translation_service


class BarangayAIEngine:
    """AI engine for Barangay Portal chatbot with Filipino and English support"""
    
    def __init__(self):
        self.confidence_threshold = 0.3
        self.fallback_responses = {
            'en': [
                "I apologize, but I'm not sure about that. Can you try rephrasing your question?",
                "I'd be happy to help! Could you provide more details about what you're looking for?",
                "For specific assistance, you may want to contact our barangay office directly.",
                "Let me help you find what you need. Could you be more specific about your concern?",
            ],
            'fil': [
                "Pasensya na, hindi ko sigurado sa tanong mo. Pwede mo bang ulitin sa ibang paraan?",
                "Masaya akong tumulong! Pwede mo ba akong bigyan ng mas detalyadong impormasyon?",
                "Para sa tukoy na tulong, makipag-ugnayan ka sa aming barangay office.",
                "Tutulong ako sa iyo. Pwede mo bang maging mas tukoy sa inyong concern?",
            ]
        }
        
        self.greeting_responses = {
            'en': [
                "Hello! I'm your Barangay Portal assistant. How can I help you today?",
                "Hi there! Welcome to the Barangay Portal. What can I assist you with?",
                "Good day! I'm here to help you navigate our barangay services. What do you need?",
            ],
            'fil': [
                "Kumusta! Ako ang inyong Barangay Portal assistant. Paano kita matutulungan ngayon?",
                "Hello! Maligayang pagdating sa Barangay Portal. Ano ang maitutulong ko sa inyo?",
                "Magandang araw! Nandito ako para tumulong sa inyong mga pangangailangan. Ano ang kailangan ninyo?",
            ]
        }
        
        self.common_patterns = {
            'greeting': [
                r'\b(hi|hello|hey|kumusta|good morning|good afternoon|good evening|magandang)\b',
                r'\b(start|begin|simula)\b'
            ],
            'thanks': [
                r'\b(thank|thanks|salamat|maraming salamat)\b'
            ],
            'help': [
                r'\b(help|tulong|assist|guide|gabay)\b'
            ],
            'complaint': [
                r'\b(complaint|reklamo|problem|problema|issue|hirap|sumbong)\b'
            ],
            'services': [
                r'\b(service|serbisyo|offer|alok|available|pwede|meron)\b'
            ],
            'contact': [
                r'\b(contact|makipag-ugnayan|phone|telepono|email|address|tawagan)\b'
            ],
            'hours': [
                r'\b(hours|oras|open|bukas|close|sara|time|panahon|schedule)\b'
            ],
            'documents': [
                r'\b(document|dokumento|certificate|sertipiko|clearance|permit|papel|requirements)\b'
            ],
            'weather': [
                r'\b(weather|panahon|bagyo|typhoon|ulan|rain|init|hot|lamig|cold|klima)\b',
                r'\b(forecast|hula|prediction|ulat|report|update)\b',
                r'\b(tomorrow|bukas|next|susunod|week|linggo|today|ngayon)\b.*\b(weather|panahon|ulan|bagyo)\b',
                r'\b(maulan|umuulan|will.*rain|may.*ulan|magkakaroon.*ulan)\b',
                r'\b(magiging.*init|will.*hot|mainit.*ba|hot.*ba)\b'
            ],
            'emergency': [
                r'\b(emergency|emerhensya|urgent|kailangan|tulong|rescue|saklolo)\b'
            ]
        }

    def process_message(self, message: str, language: str = 'en', user_context: Dict = None) -> Dict:
        """Process user message and return AI response"""
        message_lower = message.lower().strip()
        
        # Check for greetings first
        if self._matches_pattern(message_lower, self.common_patterns['greeting']):
            return {
                'response': random.choice(self.greeting_responses[language]),
                'confidence': 0.9,
                'category': 'greeting',
                'suggestions': self._get_quick_suggestions(language)
            }
        
        # Check for thanks
        if self._matches_pattern(message_lower, self.common_patterns['thanks']):
            thanks_responses = {
                'en': ["You're welcome! Is there anything else I can help you with?"],
                'fil': ["Walang anuman! May iba pa bang maitutulong ko sa inyo?"]
            }
            return {
                'response': random.choice(thanks_responses[language]),
                'confidence': 0.9,
                'category': 'thanks',
                'suggestions': self._get_quick_suggestions(language)
            }
        
        # Search knowledge base
        kb_result = self._search_knowledge_base(message_lower, language)
        if kb_result['confidence'] > self.confidence_threshold:
            return kb_result
        
        # Check for weather queries first (before knowledge base for real-time data)
        if self._matches_pattern(message_lower, self.common_patterns['weather']):
            try:
                from .api_services import weather_service
                weather_alerts = weather_service.get_weather_alerts(
                    language=language, user_query=message_lower
                )
                if weather_alerts:
                    return {
                        'response': weather_alerts[0]['message'],
                        'confidence': 0.85,
                        'category': 'weather_forecast',
                        'suggestions': self._get_weather_suggestions(language)
                    }
            except Exception as e:
                # Log error but continue with other methods
                pass
        
        # Try enhanced AI responses using external APIs
        try:
            enhanced_response = smart_response_service.get_enhanced_response(
                message, language, user_context
            )
            if enhanced_response:
                return {
                    'response': enhanced_response,
                    'confidence': 0.8,
                    'category': 'ai_enhanced',
                    'suggestions': self._get_quick_suggestions(language)
                }
        except Exception as e:
            # Log error but continue with fallback
            pass
        
        # Pattern-based responses
        pattern_result = self._pattern_based_response(message_lower, language, user_context)
        if pattern_result['confidence'] > self.confidence_threshold:
            return pattern_result
        
        # Fallback response
        return {
            'response': random.choice(self.fallback_responses[language]),
            'confidence': 0.1,
            'category': 'fallback',
            'suggestions': self._get_quick_suggestions(language)
        }

    def _search_knowledge_base(self, message: str, language: str) -> Dict:
        """Search knowledge base for relevant answers with enhanced matching"""
        knowledge_items = ChatbotKnowledgeBase.objects.filter(is_active=True).order_by('-priority')
        
        best_match = None
        best_score = 0
        
        # First pass: exact keyword matching
        for item in knowledge_items:
            score = self._calculate_relevance_score(message, item)
            if score > best_score:
                best_score = score
                best_match = item
        
        # Second pass: fuzzy matching for better accuracy
        if best_score < 0.4:
            fuzzy_match, fuzzy_score = self._fuzzy_search_knowledge_base(message, knowledge_items)
            if fuzzy_score > best_score:
                best_match = fuzzy_match
                best_score = fuzzy_score
        
        if best_match and best_score > 0.25:  # Lowered threshold for better coverage
            answer = best_match.answer_fil if language == 'fil' else best_match.answer_en
            return {
                'response': answer,
                'confidence': min(best_score, 0.95),
                'category': best_match.category,
                'suggestions': self._get_category_suggestions(best_match.category, language)
            }
        
        return {'confidence': 0}

    def _calculate_relevance_score(self, message: str, kb_item: ChatbotKnowledgeBase) -> float:
        """Calculate relevance score between message and knowledge base item"""
        score = 0
        message_words = set(message.lower().split())
        
        # Check question match
        question_words = set(kb_item.question.lower().split())
        question_overlap = len(message_words.intersection(question_words))
        score += (question_overlap / max(len(question_words), 1)) * 0.4
        
        # Check keywords match
        if kb_item.keywords:
            keywords = [kw.strip().lower() for kw in kb_item.keywords.split(',')]
            for keyword in keywords:
                if keyword in message:
                    score += 0.3
                elif any(word in keyword for word in message_words):
                    score += 0.1
        
        # Category-specific boost
        if self._matches_category(message, kb_item.category):
            score += 0.2
        
        return min(score, 1.0)

    def _matches_category(self, message: str, category: str) -> bool:
        """Check if message matches specific category patterns"""
        category_patterns = {
            'complaints': self.common_patterns['complaint'],
            'services': self.common_patterns['services'],
            'contact': self.common_patterns['contact'],
            'hours': self.common_patterns['hours'],
            'documents': self.common_patterns['documents'],
        }
        
        if category in category_patterns:
            return self._matches_pattern(message, category_patterns[category])
        return False

    def _pattern_based_response(self, message: str, language: str, user_context: Dict) -> Dict:
        """Generate response based on pattern matching"""
        responses = {
            'complaint': {
                'en': "I can help you file a complaint. Our barangay handles issues like noise complaints, public disturbances, infrastructure problems, and disputes. You can submit through our online portal or visit the office during business hours (8AM-5PM, Monday-Friday). Would you like me to guide you through the online process?",
                'fil': "Matutulungan kita mag-file ng reklamo. Hinahawakan ng aming barangay ang mga isyu tulad ng ingay, gulo sa publiko, problema sa infrastructure, at alitan. Pwede ka mag-submit online o bumisita sa office (8AM-5PM, Lunes-Biyernes). Gusto mo bang gabayan kita sa online process?"
            },
            'services': {
                'en': "Barangay Basey offers: Barangay Clearance (₱50), Certificate of Residency (₱30), Business Permit assistance, Indigency Certificate (free), and community programs. Processing time is usually 1-3 days for documents. What specific service do you need?",
                'fil': "Nag-aalok ang Barangay Basey ng: Barangay Clearance (₱50), Certificate of Residency (₱30), tulong sa Business Permit, Indigency Certificate (libre), at community programs. Usually 1-3 araw ang processing ng mga dokumento. Anong specific na serbisyo ang kailangan mo?"
            },
            'contact': {
                'en': "Barangay Basey Contact Information:\n📞 Phone: (055) 543-XXXX\n📧 Email: barangaybasey@samar.gov.ph\n📍 Address: Barangay Hall, Basey, Samar\n🕐 Hours: 8AM-5PM, Monday-Friday\n⚠️ Emergency hotline: available 24/7",
                'fil': "Contact Information ng Barangay Basey:\n📞 Telepono: (055) 543-XXXX\n📧 Email: barangaybasey@samar.gov.ph\n📍 Address: Barangay Hall, Basey, Samar\n🕐 Oras: 8AM-5PM, Lunes-Biyernes\n⚠️ Emergency hotline: available 24/7"
            },
            'help': {
                'en': "I'm your Barangay Basey AI Assistant! I can help with:\n• Filing complaints & tracking status\n• Document requirements & fees\n• Office hours & contact info\n• Weather alerts & emergencies\n• Community programs & events\n• General barangay information\n\nWhat do you need help with today?",
                'fil': "Ako ang inyong Barangay Basey AI Assistant! Matutulungan kita sa:\n• Pag-file ng reklamo at status tracking\n• Requirements at bayad ng mga dokumento\n• Office hours at contact info\n• Weather alerts at emergencies\n• Community programs at events\n• General na impormasyon ng barangay\n\nAno ang kailangan mo ngayon?"
            },
            'documents': {
                'en': "Required documents for barangay services:\n• Barangay Clearance: Valid ID, ₱50 fee\n• Residency Certificate: Proof of address, Valid ID, ₱30\n• Indigency Certificate: Valid ID (free)\n• Business Permit: Business documents, Barangay clearance\n\nProcessing: 1-3 working days. Which document do you need?",
                'fil': "Kailangang dokumento para sa barangay services:\n• Barangay Clearance: Valid ID, ₱50 bayad\n• Residency Certificate: Proof of address, Valid ID, ₱30\n• Indigency Certificate: Valid ID (libre)\n• Business Permit: Business documents, Barangay clearance\n\nProcessing: 1-3 working days. Anong dokumento ang kailangan mo?"
            },
            'emergency': {
                'en': "🚨 EMERGENCY CONTACTS:\n• Barangay Emergency: (055) 543-XXXX\n• Police: 117\n• Fire Department: 116\n• Medical Emergency: 911\n• NDRRMC: 911\n\nFor immediate assistance, call the appropriate emergency number. For non-urgent barangay matters, you can file through our portal.",
                'fil': "🚨 EMERGENCY CONTACTS:\n• Barangay Emergency: (055) 543-XXXX\n• Pulis: 117\n• Bumbero: 116\n• Medical Emergency: 911\n• NDRRMC: 911\n\nPara sa immediate na tulong, tawagan ang tamang emergency number. Para sa hindi urgent na barangay matters, pwede ka mag-file sa aming portal."
            }
        }
        
        for pattern_name, patterns in self.common_patterns.items():
            if self._matches_pattern(message, patterns) and pattern_name in responses:
                return {
                    'response': responses[pattern_name][language],
                    'confidence': 0.7,
                    'category': pattern_name,
                    'suggestions': self._get_category_suggestions(pattern_name, language)
                }
        
        return {'confidence': 0}

    def _matches_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given regex patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _get_quick_suggestions(self, language: str) -> List[str]:
        """Get quick suggestion buttons for user"""
        suggestions = {
            'en': [
                "File a complaint",
                "Available services",
                "Contact information",
                "Office hours",
                "Document requirements"
            ],
            'fil': [
                "Mag-file ng reklamo",
                "Available na serbisyo",
                "Contact information",
                "Office hours",
                "Requirements ng dokumento"
            ]
        }
        return suggestions[language]

    def _get_category_suggestions(self, category: str, language: str) -> List[str]:
        """Get category-specific suggestions"""
        category_suggestions = {
            'complaints': {
                'en': ["How to file a complaint", "Complaint status", "Required documents"],
                'fil': ["Paano mag-file ng reklamo", "Status ng reklamo", "Kailangang dokumento"]
            },
            'services': {
                'en': ["Barangay clearance", "Certificate issuance", "Permits"],
                'fil': ["Barangay clearance", "Pagbibigay ng certificate", "Mga permit"]
            },
            'contact': {
                'en': ["Phone number", "Email address", "Office location"],
                'fil': ["Numero ng telepono", "Email address", "Lokasyon ng office"]
            }
        }
        
        return category_suggestions.get(category, {}).get(language, self._get_quick_suggestions(language))
    
    def _get_weather_suggestions(self, language: str) -> List[str]:
        """Get weather-specific suggestions"""
        suggestions = {
            'en': [
                "Typhoon updates",
                "3-day forecast", 
                "Rain forecast",
                "Temperature today",
                "Emergency weather alerts"
            ],
            'fil': [
                "Update sa bagyo",
                "3-araw na forecast",
                "Forecast ng ulan", 
                "Temperatura ngayon",
                "Emergency weather alerts"
            ]
        }
        return suggestions[language]
    
    def _fuzzy_search_knowledge_base(self, message: str, knowledge_items) -> tuple:
        """Fuzzy search for better knowledge base matching"""
        best_match = None
        best_score = 0
        
        message_words = set(message.lower().split())
        
        for item in knowledge_items:
            # Check similarity with question
            question_words = set(item.question.lower().split())
            question_similarity = len(message_words.intersection(question_words)) / max(len(message_words), len(question_words), 1)
            
            # Check similarity with keywords
            keyword_similarity = 0
            if item.keywords:
                keywords = [kw.strip().lower() for kw in item.keywords.split(',')]
                keyword_matches = sum(1 for kw in keywords if any(word in kw or kw in word for word in message_words))
                keyword_similarity = keyword_matches / max(len(keywords), 1)
            
            # Check similarity with answer (partial)
            answer_text = (item.answer_en + ' ' + item.answer_fil).lower()
            answer_words = set(answer_text.split())
            answer_similarity = len(message_words.intersection(answer_words)) / max(len(message_words), 1) * 0.3
            
            # Combined similarity score
            total_score = (question_similarity * 0.5) + (keyword_similarity * 0.4) + (answer_similarity * 0.1)
            
            if total_score > best_score:
                best_score = total_score
                best_match = item
        
        return best_match, best_score
