# dataentry/management/commands/list_tags.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from taggit.models import Tag


# python manage.py list_tags                    # 全部
# python manage.py list_tags --orphans-only     # 只看孤儿
# python manage.py list_tags --search healing   # 搜索名字含 healing 的
class Command(BaseCommand):
    help = "List all tags with their usage counts."

    def add_arguments(self, parser):
        parser.add_argument('--orphans-only', action='store_true')
        parser.add_argument('--search', type=str, help="Filter by name substring.")

    def handle(self, *args, **options):
        qs = Tag.objects.annotate(c=Count('taggit_taggeditem_items')).order_by('name')

        if options['orphans_only']:
            qs = qs.filter(c=0)

        if options['search']:
            qs = qs.filter(name__icontains=options['search'])

        self.stdout.write(f"Total: {qs.count()}\n")
        for t in qs:
            flag = '  ← ORPHAN' if t.c == 0 else ''
            self.stdout.write(f"{t.c:>3}  {t.name!r}{flag}")