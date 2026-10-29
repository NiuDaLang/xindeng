# scripts/

Developer helpers for inspecting the local dev DB.

These are not production commands. They run via `manage.py shell <`, not
as a management command. If one is useful enough to promote, wrap it in a
management command under `<app>/management/commands/`.

| Script | Purpose |
|--------|---------|
| `find_instant_digital_products.py` | Lists purchasable INSTANT digital variations (for the buyer walk). |
| `find_cancellable_digital_orders.py` | Lists unclaimed digital lines in cancellable orders (for the revoked walk). |
| `inspect_token_for_order.py` | Prints a token's state for a given order number. |