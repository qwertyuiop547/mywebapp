"""
Test script to create a sample complaint with image attachment
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

def create_test_image():
    """Create a simple test image"""
    # Create a simple red square image
    image = Image.new('RGB', (300, 300), color='red')
    
    # Add some text
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    draw.text((50, 150), "TEST IMAGE", fill='white')
    
    # Convert to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    return image_bytes.getvalue()

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
            title="Test Electrical Issue with Image",
            description="May puno dito sa amin na nakaharang na sa mga linya ng kuryente. Delikado na at baka magka-short circuit. Lalo na kapag malakas ang hangin. (TEST COMPLAINT)",
            location="Barangay Street, Burgos",
            priority="high"
        )
        
        # Create test image
        image_data = create_test_image()
        
        # Create attachment
        attachment = ComplaintAttachment.objects.create(
            complaint=complaint,
            file_name="electrical_issue_sample.png",
            file_type="image"
        )
        
        # Save the image file
        attachment.file.save(
            "electrical_issue_sample.png",
            ContentFile(image_data),
            save=True
        )
        
        print(f"✅ Successfully created test complaint #{complaint.id} with image attachment")
        print(f"   Title: {complaint.title}")
        print(f"   Attachment: {attachment.file.name}")
        print(f"   File URL: {attachment.file.url}")
        
    except Exception as e:
        print(f"❌ Error creating test complaint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()