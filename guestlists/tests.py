from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from events.models import Event
from .forms import AdminGuestEntryForm, GuestEntryForm
from .models import GuestEntry


class OptionalGuestlistCreationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin",password="password",role=User.Role.ADMIN)
        self.client.force_login(self.admin)

    def test_admin_form_has_no_promoter_and_all_fields_are_optional(self):
        form=AdminGuestEntryForm()

        self.assertNotIn("promoter",form.fields)
        self.assertTrue(all(not field.required for field in form.fields.values()))

    def test_admin_can_submit_completely_blank_guestlist(self):
        response=self.client.post(reverse("guestlists:admin_create"),{
            "guests-TOTAL_FORMS":"1",
            "guests-INITIAL_FORMS":"0",
            "guests-MIN_NUM_FORMS":"0",
            "guests-MAX_NUM_FORMS":"1000",
        })

        self.assertRedirects(response,reverse("guestlists:admin_list"))
        entry=GuestEntry.objects.get()
        self.assertIsNone(entry.promoter)
        self.assertIsNone(entry.event)
        self.assertIsNone(entry.pass_type)
        self.assertEqual(entry.guest_name,"")
        self.assertIsNone(entry.amount_paid)

    def test_promoter_form_fields_are_all_optional(self):
        form=GuestEntryForm(user=None)

        self.assertTrue(all(not field.required for field in form.fields.values()))

    def test_promoter_can_submit_completely_blank_guestlist(self):
        promoter=User.objects.create_user(username="promoter",password="password",role=User.Role.MEMBER)
        self.client.force_login(promoter)

        response=self.client.post(reverse("guestlists:member_create"),{
            "guests-TOTAL_FORMS":"1",
            "guests-INITIAL_FORMS":"0",
            "guests-MIN_NUM_FORMS":"0",
            "guests-MAX_NUM_FORMS":"1000",
        })

        self.assertRedirects(response,reverse("guestlists:member_list"))
        entry=GuestEntry.objects.get(promoter=promoter)
        self.assertIsNone(entry.event)
        self.assertIsNone(entry.pass_type)
        self.assertEqual(entry.guest_name,"")
        self.assertIsNone(entry.amount_paid)

    def test_admin_created_event_is_selectable_without_promoter_assignment(self):
        event=Event.objects.create(name="Global event",event_date="2026-08-01",start_time="20:00",status=Event.Status.DRAFT,created_by=self.admin)
        promoter=User.objects.create_user(username="unassigned",password="password",role=User.Role.MEMBER)

        promoter_form=GuestEntryForm(user=promoter)
        admin_form=AdminGuestEntryForm()

        self.assertIn(event,promoter_form.fields["event"].queryset)
        self.assertIn(event,admin_form.fields["event"].queryset)
