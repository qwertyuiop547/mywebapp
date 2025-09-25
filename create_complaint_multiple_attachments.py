"""
Create a test complaint with multiple attachments (images and documents)
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('c:\\Users\\JUSTIN\\Documents\\Project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from complaints.models import Complaint, ComplaintCategory, ComplaintAttachment
from django.core.files.base import ContentFile
from PIL import Image
import io

User = get_user_model()

def create_test_image(color, text):
    """Create a simple test image"""
    image = Image.new('RGB', (300, 300), color=color)
    
    # Add text
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((50, 150), text, fill='white', font=font)
    
    # Convert to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    return image_bytes.getvalue()

def create_test_document():
    """Create a simple test document"""
    content = """
BARANGAY INCIDENT REPORT

Date: September 20, 2025
Location: Barangay Street, Burgos
Type: Infrastructure Issue

DESCRIPTION:
May nakaharang na puno sa electrical lines na nagdudulot ng panganib.
Mataas ang risk ng short circuit lalo na kapag malakas ang hangin.

RECOMMENDED ACTION:
- Immediate tree cutting/trimming
- Inspection of electrical lines
- Safety measures implementation

Reported by: Test Resident
Contact: test@example.com
    """
    return content.encode('utf-8')

def main():
    try:
        # Get first resident user
        resident = User.objects.filter(role='resident', is_approved=True).first()
        if not resident:
            print("No approved resident found!")
            return
        
        # Get first category
        category = ComplaintCategory.objects.first()
        if not category:
            print("No complaint category found!")
            return
        
        # Create complaint
        complaint = Complaint.objects.create(
            complainant=resident,
            category=category,
            title="Multiple Evidence - Tree Blocking Power Lines",
            description="May malaking puno na nakaharang sa mga electrical wires sa aming street. Delikado ito lalo na kapag may bagyo o malakas na hangin. Natatakot kami na magka-short circuit at masunog ang mga bahay. May mga pictures ako at report document.",
            location="Corner of Main Street and Barangay Road, Burgos",
            priority="emergency"
        )
        
        # Create multiple test images
        image1_data = create_test_image('red', 'BEFORE\nTREE BLOCKING\nELECTRICAL LINES')
        image2_data = create_test_image('orange', 'CLOSE UP\nDANGEROUS\nSITUATION')
        image3_data = create_test_image('blue', 'LOCATION\nOVERVIEW')
        
        # Create test document
        doc_data = create_test_document()
        
        # Create image attachments
        attachments = [
            ('tree_blocking_before.png', image1_data, 'image'),
            ('dangerous_closeup.png', image2_data, 'image'),
            ('location_overview.png', image3_data, 'image'),
            ('incident_report.txt', doc_data, 'document'),
        ]
        
        for filename, data, file_type in attachments:
            attachment = ComplaintAttachment.objects.create(
                complaint=complaint,
                file_name=filename,
                file_type=file_type
            )
            
            attachment.file.save(
                filename,
                ContentFile(data),
                save=True
            )
            
            print(f"   ✅ Added {file_type}: {filename}")
        
        print(f"🎉 Successfully created complaint #{complaint.id} with multiple attachments")
        print(f"   Title: {complaint.title}")
        print(f"   Priority: {complaint.get_priority_display()}")
        print(f"   Total attachments: {complaint.attachments.count()}")
        print(f"   Images: {complaint.attachments.filter(file_type='image').count()}")
        print(f"   Documents: {complaint.attachments.filter(file_type='document').count()}")
        
    except Exception as e:
        print(f"❌ Error creating test complaint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()