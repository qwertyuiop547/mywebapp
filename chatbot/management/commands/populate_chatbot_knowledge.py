from django.core.management.base import BaseCommand
from chatbot.models import ChatbotKnowledgeBase


class Command(BaseCommand):
    help = 'Populate chatbot knowledge base with barangay-specific information'

    def handle(self, *args, **options):
        # Clear existing knowledge base
        ChatbotKnowledgeBase.objects.all().delete()
        
        knowledge_items = [
            # General Information - Enhanced
            {
                'category': 'general',
                'question': 'What is this portal about?',
                'answer_en': 'This is the Barangay Basey Complaint & Feedback Management System - your one-stop online portal for all barangay services. Through this portal, you can: (1) Submit and track complaints, (2) Provide feedback on barangay services, (3) Apply for barangay documents, (4) View announcements and updates, (5) Access emergency information, and (6) Communicate with barangay officials. The portal operates 24/7, making it convenient for you to access services anytime.',
                'answer_fil': 'Ito ang Barangay Basey Complaint & Feedback Management System - ang inyong one-stop online portal para sa lahat ng serbisyo ng barangay. Sa portal na ito, maaari kayong: (1) Magsumite at subaybayan ang mga reklamo, (2) Magbigay ng feedback sa mga serbisyo, (3) Mag-apply para sa mga dokumento, (4) Tingnan ang mga announcements at updates, (5) Ma-access ang emergency information, at (6) Makipag-ugnayan sa mga barangay officials. Bukas ang portal 24/7 para sa inyong convenience.',
                'keywords': 'portal, about, ano ito, barangay, system, website, tungkol, layunin, purpose',
                'priority': 10
            },
            {
                'category': 'general',
                'question': 'What services are available?',
                'answer_en': 'Barangay Basey offers comprehensive services:\n\n📄 DOCUMENTS (₱30-₱50):\n• Barangay Clearance - ₱50\n• Certificate of Residency - ₱30\n• Certificate of Indigency - FREE\n• Good Moral Certificate - ₱30\n• Business Permit Clearance\n\n🏛️ PUBLIC SERVICES:\n• Complaint resolution & mediation\n• Community programs & events\n• Disaster preparedness assistance\n• Health and wellness programs\n\n💻 ONLINE SERVICES:\n• 24/7 complaint filing\n• Real-time status tracking\n• Document application\n• Feedback submission\n\nProcessing time: 1-3 working days for most documents.',
                'answer_fil': 'Nag-aalok ang Barangay Basey ng komprehensibong serbisyo:\n\n📄 MGA DOKUMENTO (₱30-₱50):\n• Barangay Clearance - ₱50\n• Certificate of Residency - ₱30\n• Certificate of Indigency - LIBRE\n• Good Moral Certificate - ₱30\n• Business Permit Clearance\n\n🏛️ PUBLIC SERVICES:\n• Pag-resolve ng reklamo at mediation\n• Community programs at events\n• Tulong sa disaster preparedness\n• Health at wellness programs\n\n💻 ONLINE SERVICES:\n• 24/7 pag-file ng reklamo\n• Real-time status tracking\n• Pag-apply ng dokumento\n• Feedback submission\n\nProcessing time: 1-3 working days para sa karamihan ng dokumento.',
                'keywords': 'services, serbisyo, available, meron, offer, ano ang, clearance, certificate, permit, indigency, documents, dokumento',
                'priority': 10
            },
            
            # Complaints Process - Enhanced
            {
                'category': 'complaints',
                'question': 'How do I file a complaint?',
                'answer_en': 'STEP-BY-STEP COMPLAINT FILING PROCESS:\n\n1️⃣ REGISTER & LOGIN:\n• Create an account if you don\'t have one\n• Verify your email and wait for account approval\n• Log in to your account\n\n2️⃣ FILE COMPLAINT:\n• Go to "Complaints" section\n• Click "Submit New Complaint"\n• Select complaint category (Noise, Infrastructure, Garbage, etc.)\n• Write detailed description\n• Attach photos/documents as evidence (optional)\n• Provide exact location\n\n3️⃣ SUBMIT & TRACK:\n• Review and submit\n• You\'ll receive a tracking number\n• Check status anytime in your dashboard\n• Get notifications on updates\n\n⏰ Review time: 1-2 business days\n📱 Track 24/7 through your dashboard',
                'answer_fil': 'HAKBANG-SA-PAG-FILE NG REKLAMO:\n\n1️⃣ MAG-REGISTER & LOGIN:\n• Gumawa ng account kung wala pa kayo\n• I-verify ang email at maghintay ng approval\n• Mag-log in sa account\n\n2️⃣ MAG-FILE NG REKLAMO:\n• Pumunta sa "Complaints" section\n• I-click ang "Submit New Complaint"\n• Piliin ang category ng reklamo (Ingay, Infrastructure, Basura, etc.)\n• Sumulat ng detalyadong description\n• Mag-attach ng photos/documents bilang ebidensya (optional)\n• Ibigay ang exact na lokasyon\n\n3️⃣ I-SUBMIT & I-TRACK:\n• I-review at i-submit\n• Makakatanggap kayo ng tracking number\n• Tingnan ang status anytime sa dashboard\n• Makakatanggap ng notifications sa updates\n\n⏰ Review time: 1-2 business days\n📱 Track 24/7 sa inyong dashboard',
                'keywords': 'file complaint, paano mag-file, reklamo, submit, complaint process, mag-reklamo, how to complain, sumbong',
                'priority': 10
            },
            {
                'category': 'complaints',
                'question': 'What types of complaints can I file?',
                'answer_en': 'COMPLAINT CATEGORIES WE HANDLE:\n\n🔊 NOISE DISTURBANCES:\n• Loud music/karaoke\n• Construction noise\n• Barking dogs\n• Late-night parties\n\n🏗️ INFRASTRUCTURE:\n• Damaged roads/pathways\n• Streetlight issues\n• Drainage problems\n• Public facility concerns\n\n🗑️ GARBAGE & SANITATION:\n• Improper waste disposal\n• Uncollected garbage\n• Littering\n• Open burning\n\n👥 NEIGHBORHOOD DISPUTES:\n• Property boundary issues\n• Right of way concerns\n• Tree/plant complaints\n\n🌳 ENVIRONMENTAL ISSUES:\n• Illegal logging\n• Water pollution\n• Air quality concerns\n\n🚨 PUBLIC SAFETY:\n• Suspicious activities\n• Stray animals\n• Health hazards\n• Traffic concerns\n\nAll complaints are confidential and handled professionally.',
                'answer_fil': 'MGA KATEGORYA NG REKLAMO NA HAWAK NAMIN:\n\n🔊 INGAY:\n• Malakas na music/karaoke\n• Ingay ng construction\n• Tahol ng aso\n• Late-night na party\n\n🏗️ INFRASTRUCTURE:\n• Sirang kalsada/daanan\n• Problema sa ilaw\n• Problema sa drainage\n• Concern sa public facilities\n\n🗑️ BASURA AT KALINISAN:\n• Mali ang pagtapon ng basura\n• Hindi kinolekta ang basura\n• Pagtapon kung saan-saan\n• Pagsusunog ng basura\n\n👥 ALITAN SA KAPITBAHAY:\n• Usapin sa boundary\n• Right of way concerns\n• Reklamo sa puno/halaman\n\n🌳 KAPALIGIRAN:\n• Illegal na pagputol ng puno\n• Polusyon sa tubig\n• Polusyon sa hangin\n\n🚨 PUBLIC SAFETY:\n• Kahina-hinalang aktibidad\n• Stray animals\n• Health hazards\n• Traffic concerns\n\nLahat ng reklamo ay confidential at propesyonal ang pag-handle.',
                'keywords': 'types of complaints, uri ng reklamo, kategorya, noise, ingay, garbage, basura, safety, infrastructure, disputes, alitan, environmental, kapaligiran',
                'priority': 9
            },
            {
                'category': 'complaints',
                'question': 'How long does it take to process complaints?',
                'answer_en': 'COMPLAINT PROCESSING TIMELINE:\n\n📋 SUBMISSION: Instant (24/7 online)\n\n🔍 REVIEW: 1-2 business days\n• Barangay officials check details\n• Verify if issue falls under jurisdiction\n• Approve or request more info\n\n👨‍⚖️ ASSIGNMENT: Same day after approval\n• Assigned to appropriate official\n• Investigation begins\n\n⚖️ RESOLUTION: Varies by complexity\n• Simple cases: 3-7 days\n• Medium cases: 1-2 weeks\n• Complex cases: 2-4 weeks\n• Disputes requiring mediation: Up to 30 days\n\n📱 You\'ll receive notifications at every step!\n\n💡 TIP: Complete information and evidence speed up the process.',
                'answer_fil': 'TIMELINE NG PAG-PROCESS NG REKLAMO:\n\n📋 PAG-SUBMIT: Instant (24/7 online)\n\n🔍 REVIEW: 1-2 business days\n• Tini-check ng barangay officials\n• Vini-verify kung saklaw natin\n• Ina-approve o humihingi ng dagdag info\n\n👨‍⚖️ ASSIGNMENT: Same day pagkatapos ma-approve\n• Ipinapasa sa tamang official\n• Nagsisimula ang imbestigasyon\n\n⚖️ RESOLUTION: Depende sa complexity\n• Simple cases: 3-7 days\n• Medium cases: 1-2 weeks\n• Complex cases: 2-4 weeks\n• Disputes na kailangan ng mediation: Hanggang 30 days\n\n📱 Makakatanggap kayo ng notifications sa bawat step!\n\n💡 TIP: Kumpleto ang info at ebidensya para mas mabilis.',
                'keywords': 'processing time, gaano katagal, how long, review, resolution, timeline, tagal, when',
                'priority': 9
            },
            {
                'category': 'complaints',
                'question': 'How do I track my complaint status?',
                'answer_en': 'TRACKING YOUR COMPLAINT:\n\n1️⃣ LOGIN to your account\n2️⃣ Go to YOUR DASHBOARD\n3️⃣ Click on "MY COMPLAINTS" section\n4️⃣ View all your submitted complaints\n\nSTATUS MEANINGS:\n🟡 PENDING - Under review by barangay officials\n🔵 APPROVED - Complaint accepted, assigned to official\n🟢 IN PROGRESS - Being investigated/resolved\n✅ RESOLVED - Issue has been resolved\n❌ REJECTED - Not within barangay jurisdiction\n\n📧 You\'ll also receive EMAIL notifications for status changes.\n📱 Check anytime, 24/7!',
                'answer_fil': 'PAG-TRACK NG INYONG REKLAMO:\n\n1️⃣ MAG-LOGIN sa account\n2️⃣ Pumunta sa INYONG DASHBOARD\n3️⃣ I-click ang "MY COMPLAINTS" section\n4️⃣ Tingnan lahat ng nai-submit na reklamo\n\nKAHULUGAN NG STATUS:\n🟡 PENDING - Pinag-aaralan ng barangay officials\n🔵 APPROVED - Tinanggap ang reklamo, may assigned na official\n🟢 IN PROGRESS - Ini-investigate/nire-resolve\n✅ RESOLVED - Na-resolve na ang issue\n❌ REJECTED - Hindi saklaw ng barangay\n\n📧 Makakatanggap din kayo ng EMAIL notifications.\n📱 Tingnan anytime, 24/7!',
                'keywords': 'track complaint, subaybayan, status, tingnan, check, nasaan na, progress, update',
                'priority': 8
            },
            
            # Registration - Enhanced
            {
                'category': 'registration',
                'question': 'How do I register for an account?',
                'answer_en': 'ACCOUNT REGISTRATION PROCESS:\n\n1️⃣ CLICK "REGISTER":\n• Find the Register button in navigation menu\n• Or go to login page and click "Create Account"\n\n2️⃣ FILL OUT FORM:\n• Personal information (Name, Email, Phone)\n• Address in Barangay Basey (must be resident)\n• Create strong password\n• Upload profile photo (optional)\n• Agree to terms and conditions\n\n3️⃣ VERIFY EMAIL:\n• Check your email inbox\n• Click verification link\n• This confirms your email is valid\n\n4️⃣ WAIT FOR APPROVAL:\n• Barangay officials review your application\n• Usually takes 1-2 business days\n• You\'ll receive email notification\n\n5️⃣ START USING:\n• Login with your credentials\n• Access all portal features\n\n📧 Email: Required for verification\n📱 Phone: For SMS notifications (optional)',
                'answer_fil': 'PROSESO NG PAG-REGISTER:\n\n1️⃣ I-CLICK ANG "REGISTER":\n• Hanapin ang Register button sa navigation menu\n• O pumunta sa login page at i-click ang "Create Account"\n\n2️⃣ PUNAN ANG FORM:\n• Personal information (Pangalan, Email, Phone)\n• Address sa Barangay Basey (dapat residente)\n• Gumawa ng strong password\n• Mag-upload ng profile photo (optional)\n• Sumang-ayon sa terms and conditions\n\n3️⃣ I-VERIFY ANG EMAIL:\n• Tingnan ang inyong email inbox\n• I-click ang verification link\n• Ito ay para ma-confirm ang inyong email\n\n4️⃣ MAGHINTAY NG APPROVAL:\n• Rere-view ng barangay officials ang application\n• Usually 1-2 business days\n• Makakatanggap kayo ng email notification\n\n5️⃣ SIMULAN ANG PAGGAMIT:\n• Mag-login gamit ang credentials\n• Ma-access lahat ng features\n\n📧 Email: Kailangan para sa verification\n📱 Phone: Para sa SMS notifications (optional)',
                'keywords': 'register, registration, mag-register, paano mag-register, account, sign up, approval, gumawa ng account, create account',
                'priority': 10
            },
            {
                'category': 'registration',
                'question': 'Who can register for an account?',
                'answer_en': 'ELIGIBILITY REQUIREMENTS:\n\n✅ RESIDENTS OF BARANGAY BASEY:\n• Must have valid address within Barangay Basey, Samar\n• Proof of residency may be required\n\n✅ REQUIRED DOCUMENTS:\n• Valid government-issued ID\n• Proof of address (utility bill, lease contract, etc.)\n• May need barangay clearance in some cases\n\n👥 ALL AGES WELCOME:\n• 18+ can register independently\n• Minors (below 18) need parent/guardian to register\n\n🏢 ORGANIZATIONS/BUSINESSES:\n• Can register for business-related services\n• Need business registration documents\n\n⚠️ VERIFICATION PROCESS:\n• Barangay officials verify residency\n• Faster if you have existing barangay records\n• May require in-person verification for first-time residents\n\n💡 NON-RESIDENTS: Can view announcements but cannot file complaints or request documents.',
                'answer_fil': 'REQUIREMENTS PARA MAKA-REGISTER:\n\n✅ MGA RESIDENTE NG BARANGAY BASEY:\n• Dapat may valid address sa loob ng Barangay Basey, Samar\n• Maaaring kailanganin ang proof of residency\n\n✅ KAILANGANG DOKUMENTO:\n• Valid government-issued ID\n• Proof of address (utility bill, lease contract, etc.)\n• Minsan kailangan ng barangay clearance\n\n👥 LAHAT NG EDAD PWEDE:\n• 18+ pwedeng mag-register mag-isa\n• Minors (below 18) kailangan ng parent/guardian\n\n🏢 ORGANIZATIONS/BUSINESSES:\n• Pwedeng mag-register para sa business services\n• Kailangan ng business registration documents\n\n⚠️ VERIFICATION PROCESS:\n• Vini-verify ng barangay officials ang residency\n• Mas mabilis kung may existing records na\n• Minsan kailangan ng in-person verification\n\n💡 HINDI RESIDENTE: Pwede makita ang announcements pero hindi pwede mag-file ng reklamo o humingi ng dokumento.',
                'keywords': 'who can register, sino pwede, eligibility, residents, residente, requirements, verification, proof, sino ang maaaring, qualification',
                'priority': 9
            },
            {
                'category': 'registration',
                'question': 'Why is my account not approved yet?',
                'answer_en': 'ACCOUNT APPROVAL REASONS:\n\n⏰ NORMAL PROCESSING:\n• Usually takes 1-2 business days\n• Weekends and holidays not counted\n• High volume may cause delays\n\n❗ COMMON ISSUES:\n• Incomplete information provided\n• Address not within Barangay Basey\n• Email not verified yet\n• Documents unclear or missing\n• Duplicate account detected\n\n✅ WHAT TO DO:\n• Check your email for requests for more info\n• Verify all information is complete\n• Ensure address is correct\n• Contact office if > 3 business days\n\n📞 CONTACT FOR HELP:\n• Call: (055) 543-XXXX\n• Email: barangaybasey@samar.gov.ph\n• Office hours: 8AM-5PM, Mon-Fri',
                'answer_fil': 'DAHILAN NG HINDI PA NA-APPROVE:\n\n⏰ NORMAL NA PROCESSING:\n• Usually 1-2 business days\n• Hindi kasama weekends at holidays\n• Maaaring mas matagal kung maraming application\n\n❗ COMMON NA ISSUES:\n• Kulang ang information\n• Address ay wala sa Barangay Basey\n• Hindi pa na-verify ang email\n• Hindi clear o kulang ang documents\n• May duplicate account\n\n✅ ANO ANG GAGAWIN:\n• Tingnan ang email kung may request for more info\n• I-verify na kumpleto lahat\n• Siguruhin na tama ang address\n• Makipag-ugnayan sa office kung > 3 business days\n\n📞 MAKIPAG-UGNAYAN:\n• Call: (055) 543-XXXX\n• Email: barangaybasey@samar.gov.ph\n• Office hours: 8AM-5PM, Mon-Fri',
                'keywords': 'account not approved, hindi pa approved, bakit, why, pending, waiting, approval, verification',
                'priority': 7
            },
            
            # Contact Information - Enhanced
            {
                'category': 'contact',
                'question': 'What are your contact details?',
                'answer_en': 'CONTACT BARANGAY BASEY:\n\n📞 PHONE:\n• Main Office: (055) 543-XXXX\n• Emergency Hotline: (055) 543-YYYY (24/7)\n• Text/SMS: +63 (917) XXX-YYYY\n\n📧 EMAIL:\n• General Inquiries: barangaybasey@samar.gov.ph\n• Complaints: complaints@barangaybasey.gov.ph\n• Documents: documents@barangaybasey.gov.ph\n\n📍 OFFICE ADDRESS:\n• Barangay Hall, Basey, Samar\n• Near Basey Municipal Hall\n\n💻 ONLINE:\n• Portal: https://barangaybasey-portal.gov.ph\n• Facebook: @BarangayBasey Official\n\n🕐 OFFICE HOURS:\n• Monday-Friday: 8:00 AM - 5:00 PM\n• Saturday: 8:00 AM - 12:00 PM\n• Sunday/Holidays: Closed (Emergency hotline open 24/7)',
                'answer_fil': 'MAKIPAG-UGNAYAN SA BARANGAY BASEY:\n\n📞 TELEPONO:\n• Main Office: (055) 543-XXXX\n• Emergency Hotline: (055) 543-YYYY (24/7)\n• Text/SMS: +63 (917) XXX-YYYY\n\n📧 EMAIL:\n• General Inquiries: barangaybasey@samar.gov.ph\n• Mga Reklamo: complaints@barangaybasey.gov.ph\n• Mga Dokumento: documents@barangaybasey.gov.ph\n\n📍 ADDRESS NG OFFICE:\n• Barangay Hall, Basey, Samar\n• Malapit sa Basey Municipal Hall\n\n💻 ONLINE:\n• Portal: https://barangaybasey-portal.gov.ph\n• Facebook: @BarangayBasey Official\n\n🕐 OFFICE HOURS:\n• Monday-Friday: 8:00 AM - 5:00 PM\n• Saturday: 8:00 AM - 12:00 PM\n• Sunday/Holidays: Sarado (Emergency hotline bukas 24/7)',
                'keywords': 'contact, makipag-ugnayan, phone, telepono, email, address, location, saan, where, numero, number',
                'priority': 10
            },
            {
                'category': 'contact',
                'question': 'Where is the barangay office located?',
                'answer_en': 'BARANGAY BASEY OFFICE LOCATION:\n\n📍 ADDRESS:\n• Barangay Hall, Basey, Samar\n• Poblacion area\n• Near Basey Municipal Hall\n• Beside the public market\n\n🚗 HOW TO GET THERE:\n• From Tacloban: Take bus to Basey (1 hour)\n• From Town Center: 5-minute walk\n• Jeepney routes: All Basey routes pass by\n\n🅿️ PARKING:\n• Public parking available\n• Free for residents\n\n🏛️ NEARBY LANDMARKS:\n• Basey Municipal Hall\n• Public Market\n• Basey Church\n• Basey Elementary School\n\n🗺️ GPS COORDINATES:\n• Latitude: 11.2793° N\n• Longitude: 125.0644° E\n\n💡 TIP: Visible from main road, look for the Philippine flag!',
                'answer_fil': 'LOKASYON NG BARANGAY BASEY OFFICE:\n\n📍 ADDRESS:\n• Barangay Hall, Basey, Samar\n• Area ng Poblacion\n• Malapit sa Basey Municipal Hall\n• Tabi ng public market\n\n🚗 PAANO PUMUNTA:\n• Galing Tacloban: Sumakay ng bus to Basey (1 oras)\n• Galing Town Center: 5-minute na lakad\n• Jeepney routes: Lahat ng Basey routes dumadaan\n\n🅿️ PARKING:\n• May public parking\n• Libre para sa residents\n\n🏛️ MGA LANDMARK SA PALIGID:\n• Basey Municipal Hall\n• Public Market\n• Basey Church\n• Basey Elementary School\n\n🗺️ GPS COORDINATES:\n• Latitude: 11.2793° N\n• Longitude: 125.0644° E\n\n💡 TIP: Kita sa main road, hanapin ang Philippine flag!',
                'keywords': 'office location, nasaan, saan, where, address, location, map, directions, paano pumunta, landmark',
                'priority': 9
            },
            
            # Office Hours - Enhanced
            {
                'category': 'hours',
                'question': 'What are your office hours?',
                'answer_en': 'BARANGAY BASEY OFFICE HOURS:\n\n🏢 REGULAR HOURS:\n📅 Monday - Friday: 8:00 AM - 5:00 PM\n📅 Saturday: 8:00 AM - 12:00 PM (Noon)\n\n🚫 CLOSED:\n• Sundays\n• National Holidays\n• Special Non-Working Days\n\n⏰ LUNCH BREAK:\n• 12:00 PM - 1:00 PM (Skeleton crew only)\n\n🚨 EMERGENCY SERVICES:\n• Available 24/7\n• Call emergency hotline: (055) 543-YYYY\n\n💻 ONLINE PORTAL:\n• Available 24/7 for:\n  - Filing complaints\n  - Checking status\n  - Viewing announcements\n  - Submitting feedback\n\n📝 DOCUMENT PROCESSING:\n• Submit anytime online\n• Claim during office hours\n• Processing: 1-3 business days\n\n💡 BEST TIME TO VISIT:\n• Early morning (8-10 AM) - Less crowded\n• Avoid lunch hour\n• Friday afternoons usually busy',
                'answer_fil': 'OFFICE HOURS NG BARANGAY BASEY:\n\n🏢 REGULAR NA ORAS:\n📅 Lunes - Biyernes: 8:00 AM - 5:00 PM\n📅 Sabado: 8:00 AM - 12:00 PM (Tanghali)\n\n🚫 SARADO:\n• Linggo\n• National Holidays\n• Special Non-Working Days\n\n⏰ LUNCH BREAK:\n• 12:00 PM - 1:00 PM (Skeleton crew lang)\n\n🚨 EMERGENCY SERVICES:\n• Available 24/7\n• Tawagan: (055) 543-YYYY\n\n💻 ONLINE PORTAL:\n• Bukas 24/7 para sa:\n  - Pag-file ng reklamo\n  - Pag-check ng status\n  - Pagtingin ng announcements\n  - Pag-submit ng feedback\n\n📝 DOCUMENT PROCESSING:\n• Pwede mag-submit anytime online\n• Claim sa office hours\n• Processing: 1-3 business days\n\n💡 BEST TIME NA BUMISITA:\n• Early morning (8-10 AM) - Konting tao\n• Iwasan ang lunch hour\n• Friday afternoons usually maraming tao',
                'keywords': 'office hours, oras, open, bukas, close, sarado, schedule, time, kailan bukas, operating hours, work hours',
                'priority': 10
            },
            
            # Documents - Enhanced
            {
                'category': 'documents',
                'question': 'What documents are required for barangay clearance?',
                'answer_en': 'BARANGAY CLEARANCE REQUIREMENTS:\n\n📋 REQUIRED DOCUMENTS:\n1. Valid Government-Issued ID (Original + Photocopy)\n   • Driver\'s License\n   • Passport\n   • SSS/UMID\n   • Postal ID\n   • PhilHealth ID\n\n2. Proof of Residency\n   • Utility bill (recent)\n   • Lease contract\n   • Barangay Certificate (if new resident)\n\n3. Completed Application Form\n   • Available at office or download online\n\n4. 2x2 ID Photo (1 piece)\n\n5. Payment: ₱50\n\n📝 FOR SPECIFIC PURPOSES (Additional):\n• Employment: Company request letter\n• Loan: Bank requirements\n• Business: Business registration docs\n• Travel: Passport copy\n\n⏰ PROCESSING TIME: 1-2 days\n\n🚶 WALK-IN or 💻 ONLINE APPLICATION:\n• Both accepted\n• Online is faster\n\n💡 TIP: Bring original IDs for verification!',
                'answer_fil': 'REQUIREMENTS PARA SA BARANGAY CLEARANCE:\n\n📋 KAILANGANG DOKUMENTO:\n1. Valid Government-Issued ID (Original + Photocopy)\n   • Driver\'s License\n   • Passport\n   • SSS/UMID\n   • Postal ID\n   • PhilHealth ID\n\n2. Proof of Residency\n   • Utility bill (recent)\n   • Lease contract\n   • Barangay Certificate (kung bagong residente)\n\n3. Completed Application Form\n   • Available sa office o i-download online\n\n4. 2x2 ID Photo (1 piraso)\n\n5. Bayad: ₱50\n\n📝 PARA SA SPECIFIC NA PURPOSE (Dagdag):\n• Employment: Company request letter\n• Loan: Bank requirements\n• Business: Business registration docs\n• Travel: Passport copy\n\n⏰ PROCESSING TIME: 1-2 days\n\n🚶 WALK-IN o 💻 ONLINE APPLICATION:\n• Pwede pareho\n• Online ay mas mabilis\n\n💡 TIP: Dalhin ang original IDs para sa verification!',
                'keywords': 'documents required, requirements, barangay clearance, kailangan, ano kailangan, clearance requirements, ID',
                'priority': 10
            },
            {
                'category': 'documents',
                'question': 'How do I get a certificate of indigency?',
                'answer_en': 'CERTIFICATE OF INDIGENCY - REQUIREMENTS:\n\n📋 REQUIRED:\n1. Valid ID (Original + Photocopy)\n2. Proof of Address\n3. Completed Application Form\n4. Recent photo (2x2, 1 piece)\n\n👥 SUPPORTING DOCUMENTS (if available):\n• Income tax return (ITR) showing low income\n• Certificate of No Income\n• DSWD certification\n• Medical records/hospital bills (for medical assistance)\n• School records (for educational assistance)\n\n👤 WITNESS REQUIREMENT:\n• 2 witnesses from same barangay\n• Must have valid IDs\n• Will sign affidavit\n\n💵 FEE: FREE (Indigency certificate is free of charge)\n\n📝 PURPOSE:\n• Medical assistance\n• Educational assistance\n• Legal aid\n• Burial assistance\n• Other social welfare programs\n\n⏰ PROCESSING: 1-2 days\n\n⚠️ VALIDITY: 6 months from issuance\n\n💡 INTERVIEW: Brief interview may be conducted to verify financial status.',
                'answer_fil': 'CERTIFICATE OF INDIGENCY - REQUIREMENTS:\n\n📋 KAILANGAN:\n1. Valid ID (Original + Photocopy)\n2. Proof of Address\n3. Completed Application Form\n4. Recent photo (2x2, 1 piraso)\n\n👥 SUPPORTING DOCUMENTS (kung meron):\n• Income tax return (ITR) na nagpapakita ng low income\n• Certificate of No Income\n• DSWD certification\n• Medical records/hospital bills (para sa medical assistance)\n• School records (para sa educational assistance)\n\n👤 WITNESS REQUIREMENT:\n• 2 witnesses from same barangay\n• Dapat may valid IDs\n• Pipirma sa affidavit\n\n💵 BAYAD: LIBRE (Walang bayad ang indigency certificate)\n\n📝 LAYUNIN:\n• Medical assistance\n• Educational assistance\n• Legal aid\n• Burial assistance\n• Iba pang social welfare programs\n\n⏰ PROCESSING: 1-2 days\n\n⚠️ VALIDITY: 6 months mula sa pag-issue\n\n💡 INTERVIEW: May maikling interview para i-verify ang financial status.',
                'keywords': 'certificate of indigency, indigency, indigency certificate, financial assistance, poverty certificate, libre, free, medical assistance, tulong',
                'priority': 9
            },
            {
                'category': 'documents',
                'question': 'How much do barangay documents cost?',
                'answer_en': 'BARANGAY DOCUMENT FEES:\n\n💰 STANDARD FEES:\n\n📄 Barangay Clearance: ₱50\n• For employment, loan, travel, etc.\n• Valid for 6 months\n\n📄 Certificate of Residency: ₱30\n• Proof of address\n• Valid for 6 months\n\n📄 Certificate of Indigency: FREE\n• For financial assistance\n• Valid for 6 months\n\n📄 Good Moral Certificate: ₱30\n• For employment, school\n• Valid for 1 year\n\n📄 Barangay ID: ₱50\n• Permanent barangay identification\n• No expiry\n\n📄 Business Permit Clearance: ₱100-₱500\n• Depends on business type/size\n\n⏰ PROCESSING TIME:\n• Regular: 1-2 days (included in fee)\n• Rush: Same day (+₱50)\n\n💵 PAYMENT METHODS:\n• Cash (office)\n• GCash/PayMaya (online)\n• Bank deposit\n\n📝 SENIOR CITIZENS & PWD:\n• 20% discount on applicable fees\n• Bring valid ID',
                'answer_fil': 'PRESYO NG MGA BARANGAY DOKUMENTO:\n\n💰 STANDARD NA BAYAD:\n\n📄 Barangay Clearance: ₱50\n• Para sa employment, loan, travel, etc.\n• Valid for 6 months\n\n📄 Certificate of Residency: ₱30\n• Proof of address\n• Valid for 6 months\n\n📄 Certificate of Indigency: LIBRE\n• Para sa financial assistance\n• Valid for 6 months\n\n📄 Good Moral Certificate: ₱30\n• Para sa employment, school\n• Valid for 1 year\n\n📄 Barangay ID: ₱50\n• Permanent barangay identification\n• Walang expiry\n\n📄 Business Permit Clearance: ₱100-₱500\n• Depende sa uri/laki ng business\n\n⏰ PROCESSING TIME:\n• Regular: 1-2 days (kasama sa bayad)\n• Rush: Same day (+₱50)\n\n💵 PARAAN NG PAGBAYAD:\n• Cash (office)\n• GCash/PayMaya (online)\n• Bank deposit\n\n📝 SENIOR CITIZENS & PWD:\n• 20% discount sa applicable fees\n• Dalhin ang valid ID',
                'keywords': 'fees, bayad, presyo, magkano, how much, cost, price, documents, clearance, certificate',
                'priority': 9
            },
            
            # Emergency - Enhanced
            {
                'category': 'emergency',
                'question': 'What are the emergency hotlines?',
                'answer_en': 'EMERGENCY HOTLINES - BARANGAY BASEY:\n\n🚨 NATIONAL EMERGENCY NUMBERS:\n• 911 - Emergency (Police, Fire, Medical)\n• 117 - Philippine National Police (PNP)\n• 116 - Bureau of Fire Protection (BFP)\n• 143 - Philippine Red Cross\n• 8888 - Citizens Complaint Hotline\n\n📞 BARANGAY BASEY EMERGENCY:\n• Main Emergency: (055) 543-YYYY (24/7)\n• Barangay Captain: +63 917 XXX-XXXX\n• Health Center: (055) 543-ZZZZ\n• Tanod/Security: +63 918 XXX-XXXX\n\n🏥 MEDICAL EMERGENCIES:\n• Basey Rural Health Unit: (055) XXX-XXXX\n• Samar Provincial Hospital: (055) XXX-YYYY\n• Eastern Samar District Hospital: (055) XXX-ZZZZ\n\n⚠️ DISASTER HOTLINES:\n• NDRRMC: 911 or (02) 8911-5061\n• PAGASA Weather: (053) 321-XXXX\n• Local MDRRMO: (055) XXX-XXXX\n\n💡 EMERGENCY TIPS:\n• Save these numbers in your phone\n• Stay calm and speak clearly\n• Know your exact location\n• Follow official instructions',
                'answer_fil': 'EMERGENCY HOTLINES - BARANGAY BASEY:\n\n🚨 NATIONAL EMERGENCY NUMBERS:\n• 911 - Emergency (Police, Fire, Medical)\n• 117 - Philippine National Police (PNP)\n• 116 - Bureau of Fire Protection (BFP)\n• 143 - Philippine Red Cross\n• 8888 - Citizens Complaint Hotline\n\n📞 BARANGAY BASEY EMERGENCY:\n• Main Emergency: (055) 543-YYYY (24/7)\n• Barangay Captain: +63 917 XXX-XXXX\n• Health Center: (055) 543-ZZZZ\n• Tanod/Security: +63 918 XXX-XXXX\n\n🏥 MEDICAL EMERGENCIES:\n• Basey Rural Health Unit: (055) XXX-XXXX\n• Samar Provincial Hospital: (055) XXX-YYYY\n• Eastern Samar District Hospital: (055) XXX-ZZZZ\n\n⚠️ DISASTER HOTLINES:\n• NDRRMC: 911 o (02) 8911-5061\n• PAGASA Weather: (053) 321-XXXX\n• Local MDRRMO: (055) XXX-XXXX\n\n💡 EMERGENCY TIPS:\n• I-save ang mga number sa phone\n• Manatiling kalmado at magsalita ng malinaw\n• Alamin ang exact location\n• Sundin ang official instructions',
                'keywords': 'emergency, emerhensya, hotlines, hotline numbers, 911, police, pulis, fire, bom bero, medical, ambulance, help, tulong, saklolo, disaster',
                'priority': 10
            },
            
            # Navigation Help - Enhanced
            {
                'category': 'navigation',
                'question': 'How do I navigate this website?',
                'answer_en': 'PORTAL NAVIGATION GUIDE:\n\n🏠 HOME PAGE:\n• View latest announcements\n• Quick access to services\n• Weather updates\n• Chat with AI assistant\n\n👤 AFTER LOGIN - Main Menu:\n\n📊 DASHBOARD:\n• Overview of your activities\n• Quick stats\n• Recent complaints\n• Notifications\n\n📝 COMPLAINTS:\n• Submit new complaint\n• Track complaint status\n• View history\n• Add comments\n\n💬 FEEDBACK:\n• Give feedback on services\n• Rate barangay performance\n• Suggestions\n\n📄 DOCUMENTS:\n• Apply for certificates\n• Check application status\n• Download approved documents\n\n🔔 NOTIFICATIONS:\n• System alerts\n• Complaint updates\n• Announcements\n\n⚙️ PROFILE:\n• Update personal info\n• Change password\n• Upload photo\n• View account history\n\n💡 TIPS:\n• Mobile-friendly design\n• Use search function\n• Check notifications regularly\n• Save frequently used pages',
                'answer_fil': 'GABAY SA PAG-NAVIGATE NG PORTAL:\n\n🏠 HOME PAGE:\n• Tingnan ang latest announcements\n• Quick access sa services\n• Weather updates\n• Chat sa AI assistant\n\n👤 PAGKATAPOS MAG-LOGIN - Main Menu:\n\n📊 DASHBOARD:\n• Overview ng activities\n• Quick stats\n• Recent complaints\n• Notifications\n\n📝 COMPLAINTS:\n• Magsumite ng bagong reklamo\n• I-track ang status\n• Tingnan ang history\n• Mag-add ng comments\n\n💬 FEEDBACK:\n• Magbigay ng feedback sa services\n• I-rate ang barangay performance\n• Mga suggestions\n\n📄 DOCUMENTS:\n• Mag-apply para sa certificates\n• Tingnan ang application status\n• I-download ang approved documents\n\n🔔 NOTIFICATIONS:\n• System alerts\n• Complaint updates\n• Announcements\n\n⚙️ PROFILE:\n• I-update ang personal info\n• Palitan ang password\n• Mag-upload ng photo\n• Tingnan ang account history\n\n💡 TIPS:\n• Mobile-friendly ang design\n• Gamitin ang search function\n• Regular na tingnan ang notifications\n• I-save ang madalas na pages',
                'keywords': 'navigate, navigation, paano gamitin, how to use, menu, dashboard, guide, gabay, website tour, paano',
                'priority': 8
            },
            {
                'category': 'navigation',
                'question': 'I forgot my password, what should I do?',
                'answer_en': 'PASSWORD RECOVERY PROCESS:\n\n1️⃣ GO TO LOGIN PAGE:\n• Click "Forgot Password?" link below login button\n\n2️⃣ ENTER EMAIL:\n• Type your registered email address\n• Click "Send Reset Link"\n\n3️⃣ CHECK EMAIL:\n• Look for password reset email\n• Check spam/junk folder if not in inbox\n• Link valid for 24 hours\n\n4️⃣ CLICK RESET LINK:\n• Opens password reset page\n• Enter new password (min. 8 characters)\n• Confirm new password\n\n5️⃣ LOGIN:\n• Use new password to login\n• Update security questions if needed\n\n⚠️ DIDN\'T RECEIVE EMAIL?\n• Check spam folder\n• Verify email address is correct\n• Wait 5 minutes and try again\n• Contact office if still no email\n\n📞 NEED HELP?\n• Call: (055) 543-XXXX\n• Email: barangaybasey@samar.gov.ph\n• Office hours: Mon-Fri 8AM-5PM\n\n💡 PASSWORD TIPS:\n• Use mix of letters, numbers, symbols\n• Avoid common passwords\n• Don\'t share your password\n• Change periodically',
                'answer_fil': 'PROSESO NG PAG-RECOVER NG PASSWORD:\n\n1️⃣ PUMUNTA SA LOGIN PAGE:\n• I-click ang "Forgot Password?" link sa ilalim ng login button\n\n2️⃣ ILAGAY ANG EMAIL:\n• I-type ang registered email address\n• I-click ang "Send Reset Link"\n\n3️⃣ TINGNAN ANG EMAIL:\n• Hanapin ang password reset email\n• Tingnan ang spam/junk folder kung wala sa inbox\n• Link valid for 24 hours\n\n4️⃣ I-CLICK ANG RESET LINK:\n• Bubuksan ang password reset page\n• Ilagay ang bagong password (min. 8 characters)\n• I-confirm ang bagong password\n\n5️⃣ MAG-LOGIN:\n• Gamitin ang bagong password\n• I-update ang security questions kung kailangan\n\n⚠️ HINDI NAKATANGGAP NG EMAIL?\n• Tingnan ang spam folder\n• I-verify na tama ang email address\n• Maghintay ng 5 minutes at subukan ulit\n• Makipag-ugnayan sa office kung wala pa rin\n\n📞 KAILANGAN NG TULONG?\n• Tawag: (055) 543-XXXX\n• Email: barangaybasey@samar.gov.ph\n• Office hours: Mon-Fri 8AM-5PM\n\n💡 PASSWORD TIPS:\n• Gumamit ng letters, numbers, symbols\n• Iwasan ang common passwords\n• Huwag ibahagi ang password\n• Palitan paminsan-minsan',
                'keywords': 'forgot password, nakalimutan, password reset, account recovery, login help, hindi makapag-login, password problem',
                'priority': 9
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
