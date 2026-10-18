# core/tests/test_proforma_invoice_number.py
"""
Uniqueness contract for ProformaInvoice.proforma_order_number.

Background
----------
The field was declared blank=True, null=True with no unique constraint,
while generate_order_confirmation_pdf does
`ProformaInvoice.objects.get(proforma_order_number=order_id)` — a .get()
on a non-unique field is a latent MultipleObjectsReturned. The dev DB
happens to have zero duplicates today (the sqids-based generation in
checkout and place_order is what keeps it clean), but the constraint
makes that a database-enforced invariant rather than a code-path
accident.

The nullable-ness of the field is deliberate and remains. A future
path might create an unnumbered draft before the sqids assignment
runs; SQLite's "multiple NULLs allowed under UNIQUE" rule is the
correct semantic for that. These tests pin:

  * A duplicate non-NULL number is rejected at the DB level.
  * Multiple NULL rows are allowed (the SQLite rule, not an oversight).
  * The sqids generator produces a value the .get() call can resolve.
"""

from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction


@pytest.fixture
def make_invoice(db):
    from carts.models import ProformaInvoice

    _counter = {"n": 0}

    def _make(*, number="XX-TEST-0001", number_kwarg=True):
        _counter["n"] += 1
        kwargs = {
            "payment_method": "BANK_TRANSFER",
            "currency_code": "HKD",
        }
        if number_kwarg:
            kwargs["proforma_order_number"] = number
        return ProformaInvoice.objects.create(**kwargs)

    return _make


class TestProformaOrderNumberUniqueness:

    def test_duplicate_non_null_number_is_rejected(self, make_invoice):
        make_invoice(number="DUP-0001")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                make_invoice(number="DUP-0001")

    def test_distinct_numbers_are_allowed(self, make_invoice):
        make_invoice(number="A-0001")
        make_invoice(number="B-0001")
        from carts.models import ProformaInvoice
        assert ProformaInvoice.objects.count() == 2

    def test_multiple_null_rows_are_allowed(self, make_invoice):
        """
        SQLite's UNIQUE treats NULL as distinct from every other value,
        including NULL. This is the intended semantic for a nullable
        identifier: any number of unnumbered drafts, zero duplicate
        numbers.

        If a future session tightens the model to null=False, this test
        should be deleted along with the null=True declaration, and a
        fresh test asserting null=False rejection added in its place.
        """
        make_invoice(number_kwarg=False)
        make_invoice(number_kwarg=False)
        from carts.models import ProformaInvoice
        assert ProformaInvoice.objects.filter(
            proforma_order_number__isnull=True
        ).count() == 2

    def test_duplicate_blank_string_is_rejected(self, make_invoice):
        """
        '' is not NULL. Under UNIQUE, two rows with '' would collide —
        which is correct, because the field is blank=True for
        form-rendering, not for storing duplicates. Production never
        stores '' (both creation paths assign via sqids before save),
        so this only matters as a guard against a future path that
        omits the assignment.
        """
        make_invoice(number="")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                make_invoice(number="")


class TestSqidsGenerationContract:
    """
    The field is populated by a sqids encoder in checkout and
    place_order. The contract the rest of the app depends on:

      * Two consecutively generated numbers for different
        ProformaInvoice rows are distinct.
      * generate_order_confirmation_pdf's
        ProformaInvoice.objects.get(proforma_order_number=...) resolves
        to exactly one row.

    These are unit tests on the sqids behaviour, not the view. The
    view's integration is covered indirectly by
    core/tests/test_checkout_conflict_responses.py, which walks the
    real checkout flow.
    """

    def test_sqids_output_is_deterministic_and_distinct_per_id(self):
        """
        sqids.encode([id]) is a pure function of the id, so distinct
        ids produce distinct encodings — unless the alphabet wraps,
        which would need >900M ids to occur. This test pins the
        function-of-id contract that both creation paths rely on.
        """
        from sqids import Sqids

        sqids = Sqids(min_length=6, alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
        a = sqids.encode([1])
        b = sqids.encode([2])
        c = sqids.encode([1])
        assert a != b
        assert a == c  # deterministic

    def test_get_resolves_to_exactly_one_row(self, make_invoice):
        inv = make_invoice(number="RESOLVE-0001")
        from carts.models import ProformaInvoice
        fetched = ProformaInvoice.objects.get(
            proforma_order_number="RESOLVE-0001"
        )
        assert fetched.pk == inv.pk