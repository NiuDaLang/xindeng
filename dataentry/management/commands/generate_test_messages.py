# dataentry/management/commands/generate_test_messages.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import ChatMessage
import random
from datetime import datetime, timedelta

Account = get_user_model()

class Command(BaseCommand):
    help = 'Generate test chat messages for performance testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'member_id', 
            type=int, 
            nargs='?',  # Optional
            default=None,
            help='Member ID to generate messages for (optional - will list members if not provided)'
        )
        parser.add_argument(
            'count', 
            type=int, 
            nargs='?',  # Optional
            default=50,  # Default to 50 messages
            help='Number of messages to generate (default: 50)'
        )
        parser.add_argument(
            '--batch-size', 
            type=int, 
            default=100, 
            help='Batch size for bulk creation'
        )
    
    def handle(self, *args, **options):
        # Safety guard
        from django.conf import settings
        if settings.DEBUG is False:
            self.stdout.write(self.style.ERROR('This command can only run in DEBUG mode!'))
            return
        
        member_id = options['member_id']
        count = options['count']
        batch_size = options['batch_size']
        
        # If no member_id provided, list available members
        if member_id is None:
            members = Account.objects.filter(is_superadmin=False)
            if not members.exists():
                self.stdout.write(self.style.ERROR('No members found'))
                return
            
            self.stdout.write(self.style.WARNING('Available members:'))
            for member in members:
                self.stdout.write(f'  ID: {member.id} - {member.username}')
            
            self.stdout.write(self.style.WARNING('\nUsage: python manage.py generate_test_messages <member_id> <count>'))
            return
        
        try:
            member = Account.objects.get(pk=member_id, is_superadmin=False)
            admin = Account.objects.filter(is_superadmin=True).first()
            
            if not admin:
                self.stdout.write(self.style.ERROR('No admin user found'))
                return
            
            self.stdout.write(f'Generating {count} messages between admin and {member.username}...')
            
            messages = []
            sample_texts = [
                "Hello, how are you?",
                "I have a question about my order",
                "Can you help me with the product?",
                "The delivery was very fast!",
                "I want to return this item",
                "Is there a discount available?",
                "Thank you for your help!",
                "When will my package arrive?",
                "The product quality is excellent",
                "I need to change my shipping address",
                "Do you have this in another color?",
                "Can I get a refund?",
                "The size is too small",
                "Great customer service!",
                "How do I track my order?",
            ]
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)
            
            for i in range(count):
                timestamp = start_time + timedelta(
                    seconds=random.randint(0, int((end_time - start_time).total_seconds()))
                )
                
                if random.choice([True, False]):
                    sender = admin
                    receiver = member
                else:
                    sender = member
                    receiver = admin
                
                content = random.choice(sample_texts) + f" [Test message {i+1}]"
                is_read = random.choice([True, False])
                
                message = ChatMessage(
                    sender=sender,
                    receiver=receiver,
                    content=content,
                    is_read=is_read,
                    timestamp=timestamp
                )
                messages.append(message)
                
                if len(messages) >= batch_size:
                    ChatMessage.objects.bulk_create(messages)
                    messages = []
                    self.stdout.write(f'Created {min(i+1, count)} messages...')
            
            if messages:
                ChatMessage.objects.bulk_create(messages)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created {count} test messages'))
            
        except Account.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Member with ID {member_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))