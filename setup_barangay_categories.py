import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from complaints.models import ComplaintCategory, CategoryAssignmentRule

# Clear existing data
CategoryAssignmentRule.objects.all().delete()
ComplaintCategory.objects.all().delete()

categories_data = [
    {
        'category': {
            'name': 'Peace & Order',
            'description': 'Noise complaints, disturbances, minor disputes, public order issues'
        },
        'assignment': {
            'default_assignee_role': 'tanod_head',
            'backup_assignee_role': 'kagawad_peace',
            'escalation_notes': 'For criminal matters, escalate to PNP. For disputes, route to Lupon Tagapamayapa.'
        }
    },
    {
        'category': {
            'name': 'Civil Disputes',
            'description': 'Boundary disputes, neighbor conflicts, property issues, mediation requests'
        },
        'assignment': {
            'default_assignee_role': 'lupon_chair',
            'backup_assignee_role': 'lupon_member',
            'escalation_notes': 'Handle per Katarungang Pambarangay (RA 7160). Escalate to courts if non-compoundable.'
        }
    },
    {
        'category': {
            'name': 'Sanitation & Garbage',
            'description': 'Garbage collection, illegal dumping, unsanitary conditions, pest control'
        },
        'assignment': {
            'default_assignee_role': 'kagawad_sanitation',
            'backup_assignee_role': 'kagawad_environment',
            'escalation_notes': 'Coordinate with City Environment Office (CENRO/MENRO) for major violations.'
        }
    },
    {
        'category': {
            'name': 'Infrastructure & Public Works',
            'description': 'Road repairs, drainage, streetlights, sidewalks, public facilities'
        },
        'assignment': {
            'default_assignee_role': 'kagawad_infra',
            'backup_assignee_role': 'secretary',
            'escalation_notes': 'Major repairs: City Engineering/DPWH. Streetlights: Electric utility (MERALCO).'
        }
    },
    {
        'category': {
            'name': 'Health Services',
            'description': 'Clinic services, health programs, sanitation complaints, public health concerns'
        },
        'assignment': {
            'default_assignee_role': 'bhw',
            'backup_assignee_role': 'kagawad_health',
            'escalation_notes': 'Escalate to RHU/City Health Office. Emergencies: EMS/PNP/Fire.'
        }
    },
    {
        'category': {
            'name': 'Social Services',
            'description': 'Aid programs, assistance for vulnerable residents, social welfare concerns'
        },
        'assignment': {
            'default_assignee_role': 'kagawad_social',
            'backup_assignee_role': 'secretary',
            'escalation_notes': 'Coordinate with MSWDO/CSWDO for assistance programs.'
        }
    },
    {
        'category': {
            'name': 'Disaster & Emergency',
            'description': 'Flooding, fallen trees, emergency preparedness, calamity response'
        },
        'assignment': {
            'default_assignee_role': 'bdrrmc_focal',
            'backup_assignee_role': 'chairman',
            'escalation_notes': 'Major disasters: MDRRMO/CDRRMO, DPWH, Fire Department.'
        }
    },
    {
        'category': {
            'name': 'Youth & Sports',
            'description': 'Youth programs, sports facilities, SK events, peer disputes (non-criminal)'
        },
        'assignment': {
            'default_assignee_role': 'sk_chair',
            'backup_assignee_role': 'kagawad_social',
            'escalation_notes': 'School-related: guidance counselor. Serious issues: escalate to Chairman.'
        }
    },
    {
        'category': {
            'name': 'Business & Permits',
            'description': 'Unlicensed businesses, permit violations, commercial noise, compliance issues'
        },
        'assignment': {
            'default_assignee_role': 'secretary',
            'backup_assignee_role': 'kagawad_peace',
            'escalation_notes': 'Major violations: BPLO/City Licensing Office.'
        }
    },
    {
        'category': {
            'name': 'Stray Animals',
            'description': 'Stray dogs/cats, animal control, rabies concerns, animal-related complaints'
        },
        'assignment': {
            'default_assignee_role': 'animal_control',
            'backup_assignee_role': 'kagawad_environment',
            'escalation_notes': 'Rabies cases: City Veterinarian/CVO immediately.'
        }
    },
    {
        'category': {
            'name': 'VAWC & Child Protection',
            'description': 'Violence Against Women and Children, abuse reports, protection requests'
        },
        'assignment': {
            'default_assignee_role': 'vaw_officer',
            'backup_assignee_role': 'chairman',
            'is_sensitive': True,
            'escalation_notes': 'Follow RA 9262/RA 7610. Escalate: PNP-WCPD, MSWDO. Maintain confidentiality.'
        }
    },
    {
        'category': {
            'name': 'Drug-Related Issues',
            'description': 'Suspected drug activities, substance abuse concerns, rehabilitation requests'
        },
        'assignment': {
            'default_assignee_role': 'badac_focal',
            'backup_assignee_role': 'chairman',
            'is_sensitive': True,
            'escalation_notes': 'Coordinate with PNP/PDEA as needed. Handle with discretion.'
        }
    }
]

print("Creating categories and assignment rules...")

for item in categories_data:
    # Create category
    category = ComplaintCategory.objects.create(**item['category'])
    print(f"Created category: {category.name}")
    
    # Create assignment rule
    assignment_data = item['assignment'].copy()
    assignment_data['category'] = category
    
    # Set default values for optional fields
    if 'is_sensitive' not in assignment_data:
        assignment_data['is_sensitive'] = False
    if 'requires_referral' not in assignment_data:
        assignment_data['requires_referral'] = False
    
    rule = CategoryAssignmentRule.objects.create(**assignment_data)
    print(f"  → Assigned to: {rule.get_default_assignee_role_display()}")
    
    if rule.is_sensitive:
        print("  → ⚠️ SENSITIVE - Confidential handling required")

print(f"\n✅ Successfully created {len(categories_data)} categories with assignment rules!")
print("\nAssignment Summary:")
print("═" * 50)
for item in categories_data:
    category_name = item['category']['name']
    assignee = item['assignment']['default_assignee_role']
    backup = item['assignment'].get('backup_assignee_role', 'None')
    sensitive = "🔒 SENSITIVE" if item['assignment'].get('is_sensitive', False) else ""
    print(f"{category_name:<25} → {assignee:<15} (backup: {backup}) {sensitive}")