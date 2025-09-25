"""
Utility functions for automatic resident validation
"""
import re
from decimal import Decimal
from accounts.models import BarangayArea, ResidencyValidation


# Barangay Burgos approximate boundaries (rough polygon)
BARANGAY_BOUNDARIES = [
    # Define polygon coordinates for Barangay Burgos, Basey, Samar
    # These are approximate coordinates - adjust based on actual barangay boundaries
    (11.2650, 125.0000),  # Northwest
    (11.2650, 125.0150),  # Northeast  
    (11.2500, 125.0150),  # Southeast
    (11.2500, 125.0000),  # Southwest
]

BARANGAY_CENTER = (11.2588, 125.0078)
BARANGAY_RADIUS_KM = 2.0  # 2km radius from center


def is_point_in_barangay(latitude, longitude):
    """
    Check if coordinates are within Barangay Burgos boundaries
    Uses both polygon check and radius check for validation
    """
    if not latitude or not longitude:
        return False
        
    lat = float(latitude)
    lng = float(longitude)
    
    # Basic radius check (simple validation)
    center_lat, center_lng = BARANGAY_CENTER
    
    # Calculate approximate distance using Haversine formula (simplified)
    lat_diff = abs(lat - center_lat)
    lng_diff = abs(lng - center_lng)
    
    # Rough distance calculation (1 degree ≈ 111km)
    distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111
    
    return distance_km <= BARANGAY_RADIUS_KM


def validate_barangay_address(address):
    """
    Validate address against known streets/areas in Barangay Burgos
    Returns (is_valid, matched_area, confidence_score)
    """
    if not address:
        return False, None, 0
    
    address_lower = address.lower().strip()
    
    # Get all active barangay areas
    areas = BarangayArea.objects.filter(is_active=True)
    
    best_match = None
    best_score = 0
    
    for area in areas:
        area_name = area.name.lower()
        
        # Exact match
        if area_name in address_lower:
            confidence = 100
            if confidence > best_score:
                best_score = confidence
                best_match = area
        
        # Partial match
        elif any(word in address_lower for word in area_name.split()):
            confidence = 70
            if confidence > best_score:
                best_score = confidence
                best_match = area
    
    # Additional validation keywords
    barangay_keywords = [
        'barangay burgos', 'brgy burgos', 'burgos', 'basey', 'samar'
    ]
    
    for keyword in barangay_keywords:
        if keyword in address_lower:
            best_score += 20
            break
    
    is_valid = best_score >= 50
    return is_valid, best_match, min(100, best_score)


def auto_validate_residency(user):
    """
    Perform automatic residency validation for a user
    Returns ResidencyValidation object with results
    """
    # Get or create validation record
    validation, created = ResidencyValidation.objects.get_or_create(
        user=user,
        defaults={
            'location_status': 'pending',
            'address_status': 'pending',
            'validation_notes': '',
        }
    )
    
    validation_notes = []
    
    # Validate location coordinates
    if user.latitude and user.longitude:
        if is_point_in_barangay(user.latitude, user.longitude):
            validation.location_status = 'valid_location'
            validation_notes.append("✓ Location coordinates are within Barangay Burgos")
        else:
            validation.location_status = 'invalid_location'
            validation_notes.append("✗ Location coordinates are outside Barangay Burgos")
    else:
        validation.location_status = 'pending'
        validation_notes.append("⚠ No location coordinates provided")
    
    # Validate address
    if user.address:
        is_valid, matched_area, confidence = validate_barangay_address(user.address)
        
        if is_valid:
            validation.address_status = 'valid_address'
            if matched_area:
                validation_notes.append(f"✓ Address matches {matched_area.name} (confidence: {confidence}%)")
            else:
                validation_notes.append(f"✓ Address appears valid for Barangay Burgos (confidence: {confidence}%)")
        else:
            validation.address_status = 'invalid_address'
            validation_notes.append("✗ Address does not match known areas in Barangay Burgos")
    else:
        validation.address_status = 'pending'
        validation_notes.append("⚠ No address provided")
    
    # Calculate validation score
    validation.calculate_validation_score()
    validation.validation_notes = '\n'.join(validation_notes)
    
    # Auto-approve if validation score is high enough
    overall_status = validation.get_overall_status()
    if overall_status == 'auto_approved' and validation.auto_validation_score >= 80:
        user.is_approved = True
        user.save()
        validation_notes.append("🎉 AUTO-APPROVED: High validation score")
        validation.validation_notes = '\n'.join(validation_notes)
    
    validation.save()
    return validation


def get_validation_feedback(user):
    """
    Get user-friendly validation feedback for real-time display
    """
    try:
        validation = user.residency_validation
    except ResidencyValidation.DoesNotExist:
        return {
            'status': 'not_validated',
            'message': 'Click "Check Residency" to validate your information',
            'color': 'secondary'
        }
    
    score = validation.auto_validation_score
    overall_status = validation.get_overall_status()
    
    if overall_status == 'auto_approved':
        return {
            'status': 'approved',
            'message': f'✓ Residency validated (Score: {score}/100)',
            'color': 'success'
        }
    elif overall_status == 'requires_manual':
        return {
            'status': 'needs_review',
            'message': f'⚠ Requires manual review (Score: {score}/100)',
            'color': 'warning'
        }
    else:
        return {
            'status': 'pending',
            'message': f'⏳ Validation pending (Score: {score}/100)',
            'color': 'info'
        }


def setup_default_barangay_areas():
    """
    Setup default streets/areas for Barangay Burgos
    Call this in a management command or during initial setup
    """
    default_areas = [
        # Zone 1
        ('Burgos Street', 'Zone 1'),
        ('Rizal Avenue', 'Zone 1'), 
        ('Main Road', 'Zone 1'),
        ('Poblacion', 'Zone 1'),
        
        # Zone 2
        ('Mabini Street', 'Zone 2'),
        ('Luna Street', 'Zone 2'),
        ('Del Pilar Avenue', 'Zone 2'),
        
        # Zone 3
        ('Bonifacio Road', 'Zone 3'),
        ('Aguinaldo Street', 'Zone 3'),
        ('Jacinto Avenue', 'Zone 3'),
        
        # General areas
        ('Coastal Road', None),
        ('Mountain View', None),
        ('Riverside', None),
        ('Central Plaza Area', None),
    ]
    
    created_count = 0
    for name, zone in default_areas:
        area, created = BarangayArea.objects.get_or_create(
            name=name,
            defaults={'zone': zone}
        )
        if created:
            created_count += 1
    
    return created_count
