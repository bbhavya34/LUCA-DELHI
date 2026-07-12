import re

from django.db import transaction

from .models import User


@transaction.atomic
def generate_luca_id(role):
    prefix = "LUCA-A-" if role == User.Role.ADMIN else "LUCA-M-"
    latest = (User.objects.select_for_update().filter(luca_id__startswith=prefix)
              .order_by("-luca_id").values_list("luca_id", flat=True).first())
    number = int(re.search(r"(\d+)$", latest).group(1)) + 1 if latest else 1
    while User.objects.filter(luca_id=f"{prefix}{number:04d}").exists():
        number += 1
    return f"{prefix}{number:04d}"
