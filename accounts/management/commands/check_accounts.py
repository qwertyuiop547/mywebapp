from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Check and display all user accounts in the system'
    
    def handle(self, *args, **options):
        all_users = User.objects.all().order_by('-date_joined')
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("📊 USER ACCOUNTS REPORT"))
        self.stdout.write("="*80)
        
        self.stdout.write(f"\n📈 Total Accounts: {all_users.count()}")
        
        # Count by status
        approved = all_users.filter(is_approved=True).count()
        pending = all_users.filter(is_approved=False).count()
        
        self.stdout.write(f"✅ Approved: {approved}")
        self.stdout.write(f"⏳ Pending: {pending}")
        
        self.stdout.write("\n" + "-"*80)
        self.stdout.write("📋 ACCOUNT DETAILS:")
        self.stdout.write("-"*80)
        
        for user in all_users:
            status = "✅ APPROVED" if user.is_approved else "⏳ PENDING"
            role = user.role.upper() if hasattr(user, 'role') else "USER"
            
            self.stdout.write(
                f"👤 {user.username:<15} | {user.email:<25} | {role:<10} | {status} | {user.date_joined.strftime('%Y-%m-%d %H:%M')}"
            )
        
        # Show recent registrations
        recent = all_users.filter(date_joined__gte=timezone.now() - timezone.timedelta(days=1))
        if recent.exists():
            self.stdout.write("\n" + "-"*80)
            self.stdout.write("🆕 RECENT REGISTRATIONS (Last 24 hours):")
            self.stdout.write("-"*80)
            
            for user in recent:
                status = "✅ APPROVED" if user.is_approved else "⏳ PENDING APPROVAL"
                self.stdout.write(f"👤 {user.username} - {user.email} - {status}")
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write("💡 TIP: Use 'python manage.py approve_all_users' to approve all pending accounts")
        self.stdout.write("="*80 + "\n")
