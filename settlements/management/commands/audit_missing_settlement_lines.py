# settlements/management/commands/audit_missing_settlement_lines.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

from orders.models import Order, OrderProduct
from settlements.models import ArtisanSettlementLine
from accounts.models import Account
from creators.models import CreatorProfile


class Command(BaseCommand):
    help = "Finds paid orders with un-settled artisan lines and emails superusers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=7,
            help="Number of days after ordering to wait before alerting. Default 7."
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print the list of missing lines without sending an email."
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        cutoff = timezone.now() - timedelta(days=days)

        eligible_orders = Order.objects.filter(
            is_ordered=True,
            ordered_at__lte=cutoff,
        ).prefetch_related('items__fulfilled_by')

        missing_lines = []

        for order in eligible_orders:
            # fulfilled_by is a ForeignKey(CreatorProfile), so the values
            # here are CreatorProfile pks, not Account pks.
            artisan_ids = set(
                order.items.filter(fulfilled_by__isnull=False)
                .values_list('fulfilled_by', flat=True)
            )
            if not artisan_ids:
                continue

            existing_artisan_ids = set(
                ArtisanSettlementLine.objects
                .filter(order=order)
                .values_list('artisan_id', flat=True)
            )

            missing_artisan_ids = artisan_ids - existing_artisan_ids
            if not missing_artisan_ids:
                continue

            # Fetch the missing CreatorProfile objects in one query per order.
            for artisan in CreatorProfile.objects.filter(id__in=missing_artisan_ids):
                missing_lines.append({
                    "order": order,
                    "artisan": artisan,
                })

        if not missing_lines:
            self.stdout.write(
                self.style.SUCCESS(f"All settled for orders older than {days} days.")
            )
            return

        subject = (
            f"[Action Required] Missing Settlement Lines for "
            f"{len(missing_lines)} artisan line(s)"
        )
        recipient_list = list(
            Account.objects
            .filter(is_superadmin=True)
            .exclude(email__isnull=True)
            .exclude(email="")
            .values_list('email', flat=True)
        )

        if not recipient_list:
            self.stdout.write(
                self.style.ERROR("No superusers with an email found to notify.")
            )
            return

        context = {
            "missing_lines": missing_lines,
            "days": days,
            "year": timezone.now().year,
        }

        html_body = render_to_string("emails/missing_settlement_lines.html", context)
        plain_body = (
            f"Missing settlement lines for {len(missing_lines)} order(s):\n\n"
        )
        for item in missing_lines:
            plain_body += (
                f"- Order: {item['order'].order_number}, "
                f"Artisan: {item['artisan'].display_name}, "
                f"Paid On: {item['order'].ordered_at:%Y-%m-%d}\n"
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — missing lines:"))
            self.stdout.write(plain_body)
            self.stdout.write(
                f"Would have emailed: {', '.join(recipient_list)}"
            )
        else:
            mail = EmailMultiAlternatives(
                subject=subject,
                body=plain_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )
            mail.attach_alternative(html_body, "text/html")
            mail.encoding = 'utf-8'
            mail.send()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(missing_lines)} missing line(s). "
                    f"Email sent to {len(recipient_list)} superuser(s)."
                )
            )