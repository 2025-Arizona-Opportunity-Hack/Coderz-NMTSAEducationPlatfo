import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from authentication.models import User
from teacher_dash.models import Course


class Command(BaseCommand):
    help = "Import basic course drafts from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--teacher-email",
            required=True,
            help="Email address of the teacher who will own the imported courses",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"]).expanduser()
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        try:
            teacher = User.objects.get(email=options["teacher_email"])
        except User.DoesNotExist as exc:
            raise CommandError(f"Teacher with email {options['teacher_email']} not found") from exc

        created = 0
        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                title = row.get("title")
                description = row.get("description", "")
                price_raw = row.get("price", "0")
                is_paid = row.get("is_paid", "false").strip().lower() in {"1", "true", "yes"}
                tags_raw = row.get("tags", "")

                if not title:
                    self.stdout.write(self.style.WARNING("Skipping row with missing title."))
                    continue

                try:
                    price = Decimal(price_raw)
                except Exception:
                    price = Decimal("0")

                course = Course.objects.create(
                    title=title,
                    description=description,
                    price=price,
                    is_paid=is_paid,
                    published_by=teacher,
                    is_published=False,
                )
                if tags_raw:
                    course.tags.add(*[tag.strip() for tag in tags_raw.split(",") if tag.strip()])
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {created} course(s)."))
