import re
import random
from typing import Dict, List, Tuple
from django.utils import timezone
from .models import ChatbotKnowledgeBase, ChatSession, ChatMessage
from .api_services import smart_response_service, weather_service, translation_service


class BarangayAIEngine:
    """AI engine for Barangay Portal chatbot with Filipino and English support"""
    
    def __init__(self):
        self.confidence_threshold = 0.25  # Lowered slightly for better coverage
        self.conversation_context = {}  # Track conversation context per session
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

    def process_message(self, message: str, language: str = 'en', user_context: Dict = None, session_id: str = None) -> Dict:
        """Process user message and return AI response with context awareness"""
        message_lower = message.lower().strip()
        
        # Auto-detect language from message if not explicitly set
        detected_language = self._detect_language(message)
        # Use detected language if different from provided
        if detected_language and detected_language != language:
            language = detected_language
        
        # Initialize session context if needed
        if session_id and session_id not in self.conversation_context:
            self.conversation_context[session_id] = {
                'last_category': None,
                'last_keywords': [],
                'message_count': 0,
                'topics_discussed': [],
                'preferred_language': language  # Remember user's language preference
            }
        
        # Update context
        if session_id:
            self.conversation_context[session_id]['message_count'] += 1
            # Update preferred language if user switches
            if language:
                self.conversation_context[session_id]['preferred_language'] = language
        
        # Check for greetings first
        if self._matches_pattern(message_lower, self.common_patterns['greeting']):
            response = self._get_personalized_greeting(language, user_context)
            if session_id:
                self.conversation_context[session_id]['last_category'] = 'greeting'
            return {
                'response': response,
                'confidence': 0.95,
                'category': 'greeting',
                'suggestions': self._get_quick_suggestions(language),
                'detected_language': language
            }
        
        # Check for thanks
        if self._matches_pattern(message_lower, self.common_patterns['thanks']):
            thanks_responses = {
                'en': ["You're welcome! Is there anything else I can help you with?"],
                'fil': ["Walang anuman! May iba pa bang maitutulong ko sa inyo?"]
            }
            return {
                'response': random.choice(thanks_responses[language]),
                'confidence': 0.95,
                'category': 'thanks',
                'suggestions': self._get_quick_suggestions(language),
                'detected_language': language
            }
        
        # Search knowledge base with context
        kb_result = self._search_knowledge_base(message_lower, language, session_id, user_context)
        if kb_result.get('confidence', 0) > self.confidence_threshold:
            # Update conversation context
            if session_id and kb_result.get('category'):
                ctx = self.conversation_context[session_id]
                ctx['last_category'] = kb_result['category']
                if kb_result['category'] not in ctx['topics_discussed']:
                    ctx['topics_discussed'].append(kb_result['category'])
            # Add detected language to response
            kb_result['detected_language'] = language
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
                        'suggestions': self._get_weather_suggestions(language),
                        'detected_language': language
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
                    'suggestions': self._get_quick_suggestions(language),
                    'detected_language': language
                }
        except Exception as e:
            # Log error but continue with fallback
            pass
        
        # Pattern-based responses
        pattern_result = self._pattern_based_response(message_lower, language, user_context)
        if pattern_result.get('confidence', 0) > self.confidence_threshold:
            pattern_result['detected_language'] = language
            return pattern_result
        
        # Fallback response
        return {
            'response': random.choice(self.fallback_responses[language]),
            'confidence': 0.1,
            'category': 'fallback',
            'suggestions': self._get_quick_suggestions(language),
            'detected_language': language
        }

    def _search_knowledge_base(self, message: str, language: str, session_id: str = None, user_context: Dict = None) -> Dict:
        """Search knowledge base for relevant answers with enhanced matching and context awareness"""
        knowledge_items = ChatbotKnowledgeBase.objects.filter(is_active=True).order_by('-priority')
        
        best_match = None
        best_score = 0
        
        # Get conversation context
        conv_context = self.conversation_context.get(session_id, {}) if session_id else {}
        last_category = conv_context.get('last_category')
        
        # First pass: exact keyword matching with context boost
        for item in knowledge_items:
            score = self._calculate_relevance_score(message, item, last_category, user_context)
            if score > best_score:
                best_score = score
                best_match = item
        
        # Second pass: fuzzy matching for better accuracy
        if best_score < 0.5:
            fuzzy_match, fuzzy_score = self._fuzzy_search_knowledge_base(message, knowledge_items, last_category)
            if fuzzy_score > best_score:
                best_match = fuzzy_match
                best_score = fuzzy_score
        
        # Third pass: semantic similarity (check for synonyms and related terms)
        if best_score < 0.4:
            semantic_match, semantic_score = self._semantic_search(message, knowledge_items, language)
            if semantic_score > best_score:
                best_match = semantic_match
                best_score = semantic_score
        
        if best_match and best_score > 0.2:  # Lowered threshold even more for better coverage
            answer = best_match.answer_fil if language == 'fil' else best_match.answer_en
            
            # Add context-aware additional info
            context_note = self._get_context_note(best_match.category, user_context, language)
            if context_note:
                answer += f"\n\n💡 {context_note}"
            
            return {
                'response': answer,
                'confidence': min(best_score, 0.98),  # Higher max confidence
                'category': best_match.category,
                'suggestions': self._get_category_suggestions(best_match.category, language),
                'kb_item_id': best_match.id
            }
        
        return {'confidence': 0}

    def _calculate_relevance_score(self, message: str, kb_item: ChatbotKnowledgeBase, last_category: str = None, user_context: Dict = None) -> float:
        """Calculate relevance score between message and knowledge base item with context awareness"""
        score = 0
        message_words = set(message.lower().split())
        
        # 1. Check question match (weighted more heavily)
        question_words = set(kb_item.question.lower().split())
        question_overlap = len(message_words.intersection(question_words))
        if len(question_words) > 0:
            question_match_ratio = question_overlap / len(question_words)
            score += question_match_ratio * 0.35
            
            # Bonus for matching important words (longer words are usually more meaningful)
            for word in message_words.intersection(question_words):
                if len(word) > 4:  # Important words are usually longer
                    score += 0.05
        
        # 2. Check keywords match (improved algorithm)
        if kb_item.keywords:
            keywords = [kw.strip().lower() for kw in kb_item.keywords.split(',')]
            keyword_matches = 0
            for keyword in keywords:
                # Exact match - highest score
                if keyword in message:
                    score += 0.25
                    keyword_matches += 1
                # Partial match - medium score
                elif any(word in keyword or keyword in word for word in message_words if len(word) > 2):
                    score += 0.15
                    keyword_matches += 1
                # Word-level match - lower score  
                elif any(word in keyword.split() for word in message_words):
                    score += 0.08
                    keyword_matches += 1
            
            # Bonus for multiple keyword matches
            if keyword_matches > 2:
                score += 0.1
        
        # 3. Category-specific boost
        if self._matches_category(message, kb_item.category):
            score += 0.15
        
        # 4. Context boost - if continuing same topic
        if last_category and kb_item.category == last_category:
            score += 0.15
        
        # 5. Priority boost - higher priority items get small boost
        if kb_item.priority >= 9:
            score += 0.05
        elif kb_item.priority >= 7:
            score += 0.03
        
        # 6. User context boost
        if user_context:
            # Boost certain categories based on user role
            user_role = user_context.get('role', 'resident')
            if user_role == 'resident':
                if kb_item.category in ['complaints', 'services', 'documents']:
                    score += 0.05
            elif user_role in ['official', 'admin']:
                if kb_item.category in ['general', 'emergency', 'navigation']:
                    score += 0.03
        
        # 7. Answer relevance check (lightweight)
        answer_text = (kb_item.answer_en + ' ' + kb_item.answer_fil).lower()
        answer_word_matches = len(message_words.intersection(set(answer_text.split())))
        if answer_word_matches > 0:
            score += min(answer_word_matches * 0.02, 0.1)  # Cap at 0.1
        
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
    
    def _fuzzy_search_knowledge_base(self, message: str, knowledge_items, last_category: str = None) -> tuple:
        """Fuzzy search for better knowledge base matching with context awareness"""
        best_match = None
        best_score = 0
        
        message_words = set(message.lower().split())
        
        for item in knowledge_items:
            # Check similarity with question
            question_words = set(item.question.lower().split())
            if len(message_words) > 0 and len(question_words) > 0:
                # Jaccard similarity
                intersection = len(message_words.intersection(question_words))
                union = len(message_words.union(question_words))
                question_similarity = intersection / union if union > 0 else 0
                
                # Boost for longer matching words
                long_word_matches = sum(1 for word in message_words.intersection(question_words) if len(word) > 4)
                question_similarity += long_word_matches * 0.05
            else:
                question_similarity = 0
            
            # Check similarity with keywords (improved)
            keyword_similarity = 0
            if item.keywords:
                keywords = [kw.strip().lower() for kw in item.keywords.split(',')]
                exact_matches = sum(1 for kw in keywords if kw in message)
                partial_matches = sum(1 for kw in keywords if any(word in kw or kw in word for word in message_words if len(word) > 2))
                
                if len(keywords) > 0:
                    keyword_similarity = (exact_matches * 0.8 + partial_matches * 0.4) / len(keywords)
            
            # Check similarity with answer (partial - to catch edge cases)
            answer_text = (item.answer_en + ' ' + item.answer_fil).lower()
            answer_words = set(answer_text.split())
            if len(message_words) > 0:
                answer_similarity = len(message_words.intersection(answer_words)) / len(message_words) * 0.2
            else:
                answer_similarity = 0
            
            # Context boost
            context_boost = 0.15 if last_category and item.category == last_category else 0
            
            # Combined similarity score with adjusted weights
            total_score = (question_similarity * 0.45) + (keyword_similarity * 0.45) + (answer_similarity * 0.1) + context_boost
            
            # Priority bonus
            if item.priority >= 9:
                total_score += 0.05
            
            if total_score > best_score:
                best_score = total_score
                best_match = item
        
        return best_match, best_score
    
    def _semantic_search(self, message: str, knowledge_items, language: str) -> tuple:
        """Semantic search using common synonyms and related terms"""
        best_match = None
        best_score = 0
        
        # Define synonym mappings for common terms
        synonyms = {
            'en': {
                'file': ['submit', 'send', 'lodge', 'report', 'create'],
                'complaint': ['problem', 'issue', 'concern', 'report', 'grievance'],
                'register': ['signup', 'create account', 'join', 'enroll'],
                'track': ['check', 'monitor', 'view', 'status', 'see', 'follow'],
                'cost': ['price', 'fee', 'charge', 'amount', 'payment'],
                'hours': ['time', 'schedule', 'open', 'operate', 'available'],
                'location': ['address', 'where', 'place', 'located'],
                'help': ['assist', 'support', 'guide', 'aid'],
                'requirements': ['documents', 'needed', 'required', 'need'],
                'contact': ['reach', 'call', 'email', 'phone'],
            },
            'fil': {
                'mag-file': ['magsumite', 'magpadala', 'mag-report', 'magreklamo'],
                'reklamo': ['problema', 'isyu', 'concern', 'hinaing', 'sumbong'],
                'mag-register': ['gumawa ng account', 'sumali', 'mag-signup'],
                'tingnan': ['check', 'subaybayan', 'monitor', 'status'],
                'presyo': ['bayad', 'halaga', 'singil', 'fee'],
                'oras': ['schedule', 'bukas', 'sarado', 'time'],
                'nasaan': ['saan', 'address', 'lokasyon', 'lugar'],
                'tulong': ['assist', 'help', 'gabay', 'suporta'],
                'kailangan': ['requirements', 'dokumento', 'needed'],
                'makipag-ugnayan': ['tawag', 'email', 'contact'],
            }
        }
        
        # Expand message with synonyms
        message_lower = message.lower()
        expanded_terms = set(message_lower.split())
        
        for term, syns in synonyms.get(language, {}).items():
            if term in message_lower:
                expanded_terms.update(syns)
            for syn in syns:
                if syn in message_lower:
                    expanded_terms.add(term)
                    expanded_terms.update(syns)
        
        # Search with expanded terms
        for item in knowledge_items:
            item_text = f"{item.question} {item.keywords} {item.answer_en if language == 'en' else item.answer_fil}".lower()
            
            matches = sum(1 for term in expanded_terms if term in item_text and len(term) > 2)
            if matches > 0:
                score = min(matches * 0.15, 0.8)  # Cap at 0.8
                
                # Boost for category match
                if self._matches_category(message_lower, item.category):
                    score += 0.1
                
                if score > best_score:
                    best_score = score
                    best_match = item
        
        return best_match, best_score
    
    def _get_context_note(self, category: str, user_context: Dict, language: str) -> str:
        """Get context-aware additional note based on category and user context"""
        if not user_context:
            return ""
        
        is_verified = user_context.get('is_verified', False)
        user_role = user_context.get('role', 'resident')
        
        notes = {
            'en': {
                'complaints': "Note: You must be logged in to file a complaint." if not is_verified else "",
                'documents': "Note: Document requests require verified account." if not is_verified else "",
                'registration': "",  # No special note needed
                'services': "Tip: Most services can be accessed 24/7 through this portal!",
            },
            'fil': {
                'complaints': "Note: Kailangan naka-login para mag-file ng reklamo." if not is_verified else "",
                'documents': "Note: Kailangan ng verified account para sa dokumento." if not is_verified else "",
                'registration': "",
                'services': "Tip: Karamihan sa services ay pwede i-access 24/7 sa portal na ito!",
            }
        }
        
        return notes.get(language, {}).get(category, "")
    
    def _get_personalized_greeting(self, language: str, user_context: Dict = None) -> str:
        """Get personalized greeting based on user context"""
        if user_context and user_context.get('username'):
            username = user_context['username']
            if language == 'fil':
                greetings = [
                    f"Kumusta {username}! Ako ang inyong Barangay Basey assistant. Paano kita matutulungan ngayon?",
                    f"Magandang araw {username}! Ano ang maitutulong ko sa inyo ngayon?",
                ]
            else:
                greetings = [
                    f"Hello {username}! I'm your Barangay Basey assistant. How can I help you today?",
                    f"Hi {username}! Welcome back. What can I assist you with?",
                ]
            return random.choice(greetings)
        else:
            # Use default greeting
            return random.choice(self.greeting_responses[language])
    
    def _detect_language(self, message: str) -> str:
        """Detect language of the message (Filipino or English)"""
        message_lower = message.lower()
        
        # Common Filipino words/particles that are strong indicators
        filipino_indicators = [
            # Questions words
            'ano', 'paano', 'saan', 'nasaan', 'kailan', 'bakit', 'sino', 'alin',
            'gaano', 'magkano', 'ilan',
            
            # Common verbs
            'gusto', 'kailangan', 'pwede', 'dapat', 'maaari', 'ayaw',
            'mag-file', 'magsumite', 'magtanong', 'magbayad',
            
            # Common particles and conjunctions
            'ba', 'po', 'nga', 'naman', 'din', 'rin', 'na', 'pa',
            'at', 'pero', 'kasi', 'kaya', 'kung', 'kapag',
            
            # Common nouns
            'reklamo', 'dokumento', 'bayad', 'oras', 'araw', 'gabi',
            'tanong', 'sagot', 'tulong', 'serbisyo',
            
            # Common adjectives
            'mabuti', 'masama', 'mahal', 'mura', 'mabilis', 'mabagal',
            
            # Pronouns
            'ako', 'ikaw', 'kami', 'tayo', 'sila', 'nila', 'natin',
            'ko', 'mo', 'niya', 'namin', 'ninyo',
            
            # Common phrases
            'kumusta', 'salamat', 'pasensya', 'paumanhin', 'opo', 'hindi',
            'oo', 'wala', 'meron', 'may', 'walang',
        ]
        
        # Common English words (that are less common in Filipino)
        english_indicators = [
            'how', 'what', 'where', 'when', 'why', 'who', 'which',
            'the', 'is', 'are', 'can', 'could', 'would', 'should',
            'want', 'need', 'have', 'has', 'will', 'do', 'does',
            'complaint', 'file', 'submit', 'register', 'track',
            'document', 'certificate', 'clearance', 'fee', 'cost',
            'office', 'hours', 'help', 'assist', 'thank', 'thanks',
        ]
        
        # Count indicators
        filipino_count = 0
        english_count = 0
        
        message_words = message_lower.split()
        
        for word in message_words:
            # Check Filipino indicators
            if word in filipino_indicators:
                filipino_count += 2  # Weight Filipino indicators more heavily
            # Check for Filipino affixes (common in Filipino verbs)
            if any(word.startswith(prefix) for prefix in ['mag', 'nag', 'pag', 'um', 'in']):
                filipino_count += 1
            if any(word.endswith(suffix) for suffix in ['an', 'in', 'han']):
                filipino_count += 1
            
            # Check English indicators
            if word in english_indicators:
                english_count += 1
        
        # Check for common Filipino question patterns
        if any(pattern in message_lower for pattern in ['ano ang', 'paano mag', 'saan ang', 'gaano ba', 'magkano ang']):
            filipino_count += 3
        
        # Check for common English question patterns
        if any(pattern in message_lower for pattern in ['how to', 'what is', 'where is', 'how much', 'how do i']):
            english_count += 2
        
        # Determine language based on counts
        if filipino_count > english_count:
            return 'fil'
        elif english_count > filipino_count:
            return 'en'
        else:
            # If tied or no strong indicators, return None (use provided language)
            return None
