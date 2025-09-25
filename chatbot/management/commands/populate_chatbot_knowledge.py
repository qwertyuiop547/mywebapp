from django.core.management.base import BaseCommand
from chatbot.models import ChatbotKnowledgeBase


class Command(BaseCommand):
    help = 'Populate chatbot knowledge base with barangay-specific information'

    def handle(self, *args, **options):
        # Clear existing knowledge base
        ChatbotKnowledgeBase.objects.all().delete()
        
        knowledge_items = [
            # General Information
            {
                'category': 'general',
                'question': 'What is this portal about?',
                'answer_en': 'This is the Barangay Burgos Complaint & Feedback Management System. It allows residents to submit complaints, provide feedback, and access barangay services online.',
                'answer_fil': 'Ito ang Barangay Burgos Complaint & Feedback Management System. Nagbibigay-daan ito sa mga residente na magsumite ng mga reklamo, magbigay ng feedback, at ma-access ang mga serbisyo ng barangay online.',
                'keywords': 'portal, about, barangay, system, website',
                'priority': 10
            },
            {
                'category': 'general',
                'question': 'What services are available?',
                'answer_en': 'Our barangay offers various services including barangay clearance, certificates of indigency, business permits, and community programs. You can also file complaints and provide feedback through this portal.',
                'answer_fil': 'Nag-aalok ang aming barangay ng iba\'t ibang serbisyo tulad ng barangay clearance, certificate of indigency, business permit, at community programs. Pwede rin kayong mag-file ng mga reklamo at magbigay ng feedback sa portal na ito.',
                'keywords': 'services, serbisyo, clearance, certificate, permit, indigency',
                'priority': 9
            },
            
            # Complaints Process
            {
                'category': 'complaints',
                'question': 'How do I file a complaint?',
                'answer_en': 'To file a complaint, you need to register first, then log in to your account. Go to the "Complaints" section and click "Submit New Complaint". Fill out the form with details about your concern and attach any supporting documents or photos.',
                'answer_fil': 'Para mag-file ng reklamo, kailangan ninyo munang mag-register, tapos mag-log in sa inyong account. Pumunta sa "Complaints" section at i-click ang "Submit New Complaint". Punan ang form ng mga detalye tungkol sa inyong concern at mag-attach ng mga supporting documents o larawan.',
                'keywords': 'file complaint, reklamo, submit, complaint process',
                'priority': 10
            },
            {
                'category': 'complaints',
                'question': 'What types of complaints can I file?',
                'answer_en': 'You can file complaints about noise disturbances, garbage disposal issues, public safety concerns, infrastructure problems, neighborhood disputes, environmental issues, and other community concerns.',
                'answer_fil': 'Pwede kayong mag-file ng mga reklamo tungkol sa ingay, problema sa basura, public safety concerns, problema sa infrastructure, gulo sa kapitbahay, environmental issues, at iba pang community concerns.',
                'keywords': 'types of complaints, noise, garbage, safety, infrastructure, disputes',
                'priority': 8
            },
            {
                'category': 'complaints',
                'question': 'How long does it take to process complaints?',
                'answer_en': 'Complaints are typically reviewed within 1-2 business days. Once approved, they are assigned to the appropriate official for resolution. The resolution time depends on the complexity of the issue.',
                'answer_fil': 'Karaniwang nire-review ang mga reklamo sa loob ng 1-2 business days. Kapag na-approve na, ipinapasa ito sa appropriate official para sa resolution. Ang resolution time ay depende sa complexity ng issue.',
                'keywords': 'processing time, how long, review, resolution',
                'priority': 7
            },
            
            # Registration
            {
                'category': 'registration',
                'question': 'How do I register for an account?',
                'answer_en': 'Click on "Register" in the navigation menu. Fill out the registration form with your personal information, including your address in Barangay Burgos. After registration, wait for account approval from barangay officials.',
                'answer_fil': 'I-click ang "Register" sa navigation menu. Punan ang registration form ng inyong personal information, kasama ang inyong address sa Barangay Burgos. Pagkatapos mag-register, maghintay ng account approval mula sa mga barangay officials.',
                'keywords': 'register, registration, account, sign up, approval',
                'priority': 9
            },
            {
                'category': 'registration',
                'question': 'Who can register for an account?',
                'answer_en': 'Only residents of Barangay Burgos can register for an account. You must provide a valid address within the barangay and may need to provide proof of residency during the verification process.',
                'answer_fil': 'Mga residente lang ng Barangay Burgos ang pwedeng mag-register ng account. Kailangan ninyong magbigay ng valid address sa loob ng barangay at maaaring kailanganin ninyong magbigay ng proof of residency sa verification process.',
                'keywords': 'who can register, residents, eligibility, verification, proof',
                'priority': 7
            },
            
            # Contact Information
            {
                'category': 'contact',
                'question': 'What are your contact details?',
                'answer_en': 'You can contact Barangay Burgos at (055) 251-2345 or email us at info@brgyburgosbasey.gov.ph. Our office is located in Burgos, Basey, Samar.',
                'answer_fil': 'Pwede ninyong makipag-ugnayan sa Barangay Burgos sa (055) 251-2345 o mag-email sa info@brgyburgosbasey.gov.ph. Ang aming office ay nasa Burgos, Basey, Samar.',
                'keywords': 'contact, phone, email, address, location, telephone',
                'priority': 8
            },
            {
                'category': 'contact',
                'question': 'Where is the barangay office located?',
                'answer_en': 'The Barangay Burgos office is located in Burgos, Basey, Samar. You can visit us during office hours for any concerns that require in-person assistance.',
                'answer_fil': 'Ang Barangay Burgos office ay nasa Burgos, Basey, Samar. Pwede kayong bumisita sa amin sa office hours para sa mga concern na kailangan ng in-person assistance.',
                'keywords': 'office location, address, where, visit, barangay hall',
                'priority': 7
            },
            
            # Office Hours
            {
                'category': 'hours',
                'question': 'What are your office hours?',
                'answer_en': 'Our office hours are Monday to Friday: 8:00 AM - 5:00 PM, Saturday: 8:00 AM - 12:00 PM. We are closed on Sundays and holidays.',
                'answer_fil': 'Ang aming office hours ay Monday to Friday: 8:00 AM - 5:00 PM, Saturday: 8:00 AM - 12:00 PM. Sarado kami sa Sunday at mga holiday.',
                'keywords': 'office hours, open, close, schedule, time, monday, friday, weekend',
                'priority': 8
            },
            
            # Documents
            {
                'category': 'documents',
                'question': 'What documents are required for barangay clearance?',
                'answer_en': 'For barangay clearance, you typically need: Valid ID, proof of residency, and completed application form. Additional requirements may apply depending on the purpose of the clearance.',
                'answer_fil': 'Para sa barangay clearance, kailangan ninyo ng: Valid ID, proof of residency, at completed application form. Maaaring may additional requirements depende sa purpose ng clearance.',
                'keywords': 'documents required, clearance, requirements, ID, proof of residency',
                'priority': 8
            },
            {
                'category': 'documents',
                'question': 'How do I get a certificate of indigency?',
                'answer_en': 'To get a certificate of indigency, visit our office with a valid ID and proof of income (or lack thereof). You may need to bring witnesses who can attest to your financial situation.',
                'answer_fil': 'Para makakuha ng certificate of indigency, bumisita sa aming office na may dalang valid ID at proof of income (o kakulangan nito). Maaaring kailangan ninyong magdala ng mga witness na makakapatunay sa inyong financial situation.',
                'keywords': 'certificate of indigency, indigency certificate, financial assistance, poverty certificate',
                'priority': 7
            },
            
            # Emergency
            {
                'category': 'emergency',
                'question': 'What are the emergency hotlines?',
                'answer_en': 'Emergency hotlines: Police - 117, Fire Department - 116, Medical Emergency - 911. For barangay emergencies, contact our office at (055) 251-2345.',
                'answer_fil': 'Emergency hotlines: Police - 117, Fire Department - 116, Medical Emergency - 911. Para sa barangay emergencies, makipag-ugnayan sa aming office sa (055) 251-2345.',
                'keywords': 'emergency, hotlines, police, fire, medical, 911, 117, 116',
                'priority': 10
            },
            
            # Navigation Help
            {
                'category': 'navigation',
                'question': 'How do I navigate this website?',
                'answer_en': 'Use the navigation menu at the top to access different sections. After logging in, you can access your dashboard, file complaints, give feedback, and manage your profile. The menu adapts based on your user role.',
                'answer_fil': 'Gamitin ang navigation menu sa taas para ma-access ang iba\'t ibang sections. Pagkatapos mag-log in, pwede ninyong ma-access ang inyong dashboard, mag-file ng complaints, magbigay ng feedback, at i-manage ang inyong profile. Nag-aadapt ang menu depende sa inyong user role.',
                'keywords': 'navigate, navigation, menu, dashboard, how to use, website guide',
                'priority': 6
            },
            {
                'category': 'navigation',
                'question': 'I forgot my password, what should I do?',
                'answer_en': 'If you forgot your password, click on "Forgot Password" on the login page. You can also contact our office at (055) 251-2345 for assistance with account recovery.',
                'answer_fil': 'Kung nakalimutan ninyo ang inyong password, i-click ang "Forgot Password" sa login page. Pwede rin kayong makipag-ugnayan sa aming office sa (055) 251-2345 para sa tulong sa account recovery.',
                'keywords': 'forgot password, password reset, account recovery, login help',
                'priority': 6
            }
        ]
        
        created_count = 0
        for item in knowledge_items:
            ChatbotKnowledgeBase.objects.create(**item)
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} knowledge base items for the chatbot.'
            )
        )
