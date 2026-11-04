# creators.models.py
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit_selectize.managers import TaggableManager
from accounts.data import DESTINATIONS_MAINLAND_CHINA
from pypinyin import slug as pinyin_slug  # add at top

# creators/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from accounts.data import DESTINATIONS_MAINLAND_CHINA


class CraftType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class CreatorProfile(models.Model):
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='creator_profile',
    )
    display_name    = models.CharField(max_length=100)
    slug            = models.SlugField(max_length=150, unique=True, blank=True)
    tagline         = models.CharField(max_length=200, blank=True)
    bio             = models.TextField(blank=True)

    province        = models.CharField(
                        max_length=50,
                        choices=DESTINATIONS_MAINLAND_CHINA,
                        blank=True,
                      )
    city            = models.CharField(max_length=50, blank=True)

    craft_types     = models.ManyToManyField(CraftType, blank=True, related_name='artisans')

    avatar          = models.ImageField(upload_to='creators/avatars/', blank=True, null=True)
    banner          = models.ImageField(upload_to='creators/banners/', blank=True, null=True)

    is_verified     = models.BooleanField(default=False)
    is_premium      = models.BooleanField(default=False)

    # 🌟 NEW: Layout selection
    PAGE_TEMPLATE_CHOICES = [
        ('A', 'Banner-Led｜橫幅主導'),
        ('B', 'Portrait-Led｜肖像主導'),
        ('C', 'Text-Led｜文本主導'),      # default
        ('D', 'Custom Premium｜客製精選'),  # admin only, requires is_premium=True
    ]
    page_template   = models.CharField(
                        max_length=2,
                        choices=PAGE_TEMPLATE_CHOICES,
                        default='C',
                        help_text="Which layout template renders this artisan's public page.",
                      )

    # 🌟 NEW: Premium custom-page metadata
    premium_page_slug       = models.SlugField(
                                max_length=80,
                                blank=True,
                                help_text="Human-readable alias for the custom premium template "
                                        "(e.g., 'atelier-lumiere'). The actual template file is "
                                        "named by pk: '<pk>_premium_page.html'.",
                              )
    premium_page_published  = models.BooleanField(
                                default=False,
                                help_text="Only render the custom premium template when True. "
                                        "Otherwise, fall back to the standard layout.",
                              )

    website         = models.URLField(blank=True)
    instagram       = models.CharField(max_length=100, blank=True)
    wechat_qr       = models.ImageField(
                        upload_to='creators/wechat_qr/',
                        blank=True,
                        null=True,
                        help_text="Upload your WeChat QR code image.｜上傳您的微信二維碼圖片。",
                      )

    dispatch_address        = models.ForeignKey(
                                'accounts.Address',
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='dispatch_for_creators',
                                help_text="Default address from which this artisan dispatches items.",
                              )

    tags = TaggableManager(blank=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_premium', 'display_name']

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.display_name) or pinyin_slug(self.display_name) or "artisan"
            self.slug = self._unique_slug(base)
        super().save(*args, **kwargs)

    def _unique_slug(self, base):
        """
        Ensure slug uniqueness. First tries `base`; on collision appends
        `-{pk}` if available, else `-{n}` counter.
        """
        base = base[:140]  # leave room for suffix
        qs = CreatorProfile.objects.filter(slug=base)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if not qs.exists():
            return base

        # Collision — use PK if we have one, else numeric counter
        if self.pk:
            return f"{base}-{self.pk}"

        n = 2
        while CreatorProfile.objects.filter(slug=f"{base}-{n}").exists():
            n += 1
        return f"{base}-{n}"

    def clean(self):
        """Model-level validation — enforced by Django admin forms."""
        super().clean()

        # Option D is reserved for premium artisans
        if self.page_template == 'D' and not self.is_premium:
            raise ValidationError({
                'page_template': "Custom layout (D) is reserved for premium artisans. "
                                 "Set 'is_premium' to True, or choose a standard layout."
            })

        # If page_template is NOT D, clear premium_page fields
        # (keeps the model tidy — flags reflect current state)
        if self.page_template != 'D':
            self.premium_page_published = False

    def get_absolute_url(self):
        return reverse('artisan_detail', kwargs={'slug': self.slug})


class ArtisanChatMessage(models.Model):
    """
    A plain-text message in a customer ↔ artisan thread.

    One thread per (artisan, customer) pair, implied by the FK
    combination — there is no Thread model in v1. Thread listing is a
    GROUP BY customer query in creators.views.dashboard_messages.

    Deliberately simpler than accounts.ChatMessage (member↔admin):

      * Image attachment is supported (added in the 3f commit for the
        CUSTOM delivery workflow — "show me the final piece before
        delivery"), but no `format_chat` URL-card filter. Plain text
        and inline URL text render as-is. A richer content renderer is
        deferred; see backlog 24 §images.
      * No WebSocket. The messages panel is server-rendered; a manual
        refresh or a form-driven reload is what picks up new messages.
      * No customer-side view in v1. This is the artisan's inbox. The
        customer's view of the same thread is a follow-on.
   
    `order_product` is nullable for the pre-purchase "Ask this
    artisan" case. When set, the message header renders
    "Re: <Product> — Variation: <X>". When null, the header is
    the customer's display name only. Guest orders — Order.user
    is SET_NULL/nullable, so a guest purchase carries only an
    email — cannot be linked; the customer must be a registered
    member for the dropdown to offer the line. See the
    2026-11-01 handoff §6 refinement for the member-only
    boundary and the guest composer note.

    Do not repoint unread_messages_count at accounts.ChatMessage.
    That model is the member↔admin channel; this one is the artisan's
    own inbox.
    """

    artisan = models.ForeignKey(
        CreatorProfile,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artisan_chat_messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_artisan_chat_messages",
    )
    content = models.TextField(max_length=2000)
    image = models.ImageField(
        upload_to="artisan_chat_images/",
        blank=True,
        null=True,
        help_text=(
            "Optional image attachment (product reference, work-in-progress "
            "preview, screenshot). Mirrors accounts.ChatMessage.image — same "
            "storage pipeline, same validation. Text-only messages remain the "
            "common case; this field exists for the cases where a picture "
            "is faster than a thousand words."
        ),
    )    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order_product = models.ForeignKey(
        "orders.OrderProduct",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_thread_messages",
        help_text=(
            "The OrderProduct this message concerns. Nullable for the "
            "pre-purchase 'Ask this artisan' case. Guest orders (no "
            "order.user) cannot be linked — the customer must be a "
            "registered member."
        ),
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["artisan", "customer", "created_at"]),
            models.Index(fields=["artisan", "is_read"]),
            models.Index(
                fields=["artisan", "order_product", "created_at"],
                name="creators_art_ordprod_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.sender.username} → {self.customer.username} "
            f"({self.artisan.display_name}): {self.content[:30]}"
        )


class ArtisanAdminMessage(models.Model):
    """
    A plain-text message in a artisan ↔ admin thread.

    One thread per artisan, implied by the FK — there is no Thread
    model in v1. Unlike ArtisanChatMessage (which is per-customer),
    the counterparty here is fixed: the platform admin. So the thread
    key is just `artisan`.

    Deliberately simpler than accounts.ChatMessage (member↔admin):

      * No image/attachment field. Content is text-only.
      * No WebSocket. The messages panel is server-rendered; a manual
        refresh or a form-driven reload is what picks up new messages.
      * No artisan-side thread picker. There is one thread — the one
        with the platform.

    is_read semantics: admin-authored messages start is_read=False
    and are flipped to True when the artisan opens the thread.
    Artisan-authored messages are created is_read=True (the sender
    has by definition read their own message).

    Do not repoint unread_messages_count (the customer thread) or
    unread_admin_messages_count (this thread) at each other. They
    are sibling counters on separate models.
    """

    artisan = models.ForeignKey(
        CreatorProfile,
        on_delete=models.CASCADE,
        related_name="admin_chat_messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_artisan_admin_messages",
    )
    content = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    source_chat_message = models.ForeignKey(
        "creators.ArtisanChatMessage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalated_admin_messages",
        help_text=(
            "The customer↔artisan message this admin escalation "
            "originated from. Null for admin-initiated threads."
        ),
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["artisan", "created_at"]),
            models.Index(fields=["artisan", "is_read"]),
        ]

    def __str__(self):
        return (
            f"{self.sender.username} → {self.artisan.display_name}: "
            f"{self.content[:30]}"
        )


class FrontlineThread(models.Model):
    """
    Admin-side visibility state for a customer↔artisan thread.

    Not a message store — the messages themselves live on
    ArtisanChatMessage, unmodified. This model exists to hold the
    per-thread state that neither the artisan-side nor the
    customer-side view can own:

      * settled_at / settled_by — the admin has reviewed the thread
        and considers it closed. Cleared automatically on any new
        message (see signal in creators/signals.py).

      * escalated_at / escalated_by — the admin has permission to
        post into this thread. Set once via the "Escalate to
        platform" button (customer or artisan side); not cleared
        by settlement, and not reverted by subsequent messages. Once
        the admin can write to a thread, they can continue to write
        to it — this matches the "read-plus-write oversight" model
        recorded in the 2026-11-02 handoff.

      * last_message_at — denormalized from the most recent
        ArtisanChatMessage.created_at, used as the indexed sort key
        for the admin's Frontline Messages list. Always advances,
        never retreats.

    Key: (artisan, customer, order_product). One thread per order
    line. A customer with two CUSTOM lines from the same artisan has
    two threads — which is the point: the admin sees them labelled
    by product+variation+order, not merged into one
    customer-artisan blob.

    Orphan handling: order_product is CASCADE, not SET_NULL. See the
    asymmetry with ArtisanChatMessage.order_product (SET_NULL) in
    the 2026-11-02 handoff §S2. If the order line vanishes, the
    thread-key object vanishes with it; the messages survive as
    detached history. Historical messages with order_product=None
    (pre-dating this model) never had a thread and do not get one
    retroactively.

    Pre-purchase threads (order_product=None on the message side)
    are NOT supported under Frontline. See handoff §D5. Enquiries
    of that shape route through the Help desk.

    Do not collapse this into ArtisanChatMessage. The thread is
    state; the message is content. Both are necessary, and only
    one of them is owned by the artisan.
    """
    artisan = models.ForeignKey(
        CreatorProfile,
        on_delete=models.CASCADE,
        related_name="frontline_threads",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="frontline_threads",
    )
    order_product = models.ForeignKey(
        "orders.OrderProduct",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="frontline_threads",
        help_text=(
            "The order line this thread concerns. Nullable only for "
            "legacy messages that pre-date this model; every new "
            "thread created by the signal carries a non-null "
            "order_product."
        ),
    )

    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Denormalized max(ArtisanChatMessage.created_at). Advanced "
            "on every message by creators.signals."
        ),
    )
    settled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Set by the admin to remove this thread from the active "
            "list. Cleared automatically on any new message."
        ),
    )
    settled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    escalated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Set when customer or artisan taps 'Escalate to platform'. "
            "Grants the admin permission to post into this thread. "
            "Not cleared by settlement."
        ),
    )
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Frontline thread"
        verbose_name_plural = "Frontline threads"
        constraints = [
            models.UniqueConstraint(
                fields=["artisan", "customer", "order_product"],
                name="unique_frontline_thread_per_line",
            ),
        ]
        indexes = [
            models.Index(fields=["-last_message_at"]),
            models.Index(fields=["settled_at", "-last_message_at"]),
            models.Index(fields=["escalated_at", "-last_message_at"]),
        ]

    def __str__(self):
        line_label = (
            str(self.order_product) if self.order_product else "(no order line)"
        )
        return (
            f"{self.customer.username} ↔ {self.artisan.display_name} "
            f"re: {line_label}"
        )

    # ── State transitions ─────────────────────────────────────────

    def mark_settled(self, by=None):
        """
        Mark this thread as settled by the admin. Idempotent — calling
        it twice does not change settled_at (keeps the earliest
        timestamp, which is the audit-relevant one).

        If the thread is currently unsettled, sets settled_at and
        settled_by. If it is already settled, this is a no-op.
        """
        from django.utils import timezone as _tz
        if self.settled_at is not None:
            return
        self.settled_at = _tz.now()
        self.settled_by = by
        self.save(update_fields=["settled_at", "settled_by", "updated_at"])

    def mark_unsettled(self):
        """
        Manually reopen this thread. Rarely needed — any new message
        from either side already triggers this via the signal. The
        explicit method exists so a view can offer "reopen" without
        requiring the user to post a message.
        """
        if self.settled_at is None:
            return
        self.settled_at = None
        self.settled_by = None
        self.save(update_fields=["settled_at", "settled_by", "updated_at"])

    def escalate(self, by):
        """
        Grant the admin write access to this thread. Idempotent — the
        first escalation wins (keeps the earliest escalated_at).

        Called from the customer-side and artisan-side "Escalate to
        platform" buttons. Not called by the admin directly: the
        admin's write access is the *result* of one of the two
        counterparties deciding the admin should join.
        """
        from django.utils import timezone as _tz
        if self.escalated_at is not None:
            return
        self.escalated_at = _tz.now()
        self.escalated_by = by
        self.save(update_fields=["escalated_at", "escalated_by", "updated_at"])

    @property
    def is_settled(self):
        return self.settled_at is not None

    @property
    def is_escalated(self):
        return self.escalated_at is not None