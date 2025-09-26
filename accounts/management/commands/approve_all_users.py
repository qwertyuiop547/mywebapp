from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Approve all pending user accounts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Actually approve the accounts (without this, it just shows what would be approved)',
        )
    
    def handle(self, *args, **options):
        pending_users = User.objects.filter(is_approved=False)
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("🔧 ACCOUNT APPROVAL TOOL"))
        self.stdout.write("="*80)
        
        if not pending_users.exists():
            self.stdout.write(self.style.SUCCESS("\n✅ No pending accounts found! All users are already approved."))
            return
        
        self.stdout.write(f"\n⏳ Found {pending_users.count()} pending accounts:")
        self.stdout.write("-"*80)
        
        for user in pending_users:
            role = user.role.upper() if hasattr(user, 'role') else "USER"
            self.stdout.write(f"👤 {user.username:<15} | {user.email:<25} | {role:<10} | Registered: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        
        if not options['confirm']:
            self.stdout.write("\n" + "="*80)
            self.stdout.write("⚠️  DRY RUN MODE - No changes made")
            self.stdout.write("🚀 To actually approve these accounts, run:")
            self.stdout.write("   python manage.py approve_all_users --confirm")
            self.stdout.write("="*80 + "\n")
            return
        
        # Actually approve the accounts
        approved_count = 0
        for user in pending_users:
            user.is_approved = True
            user.date_approved = timezone.now()
            user.save()
            approved_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Approved: {user.username} ({user.email})")
            )
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS(f"🎉 Successfully approved {approved_count} accounts!"))
        self.stdout.write("💡 These users can now login to the system.")
        self.stdout.write("="*80 + "\n")
