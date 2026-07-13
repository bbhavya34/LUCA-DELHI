from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from events.models import Event
from promoters.models import PromoterProfile
from .forms import PaymentQRCodeForm
from .models import PaymentQRCode


class PaymentEventVisibilityTests(TestCase):
    def test_member_payment_selector_includes_unassigned_event(self):
        member=User.objects.create_user(username="member-qr",password="password",role=User.Role.MEMBER)
        PromoterProfile.objects.create(user=member)
        event=Event.objects.create(name="Global event",event_date="2026-08-01",start_time="20:00",status=Event.Status.DRAFT)
        self.client.force_login(member)

        response=self.client.get(reverse("payments:member_qr"))

        self.assertContains(response,"Global event")
        self.assertEqual(response.context["event"],event)


class SharedPaymentQRTests(TestCase):
    def setUp(self):
        self.member=User.objects.create_user(username="shared-member",password="password",role=User.Role.MEMBER)
        PromoterProfile.objects.create(user=self.member)
        self.event=Event.objects.create(name="Any event",event_date="2026-08-02",start_time="21:00")

    def test_qr_upload_form_has_no_event_field(self):
        self.assertNotIn("event",PaymentQRCodeForm().fields)

    def test_member_uses_shared_qr_for_every_event(self):
        qr=PaymentQRCode.objects.create(title="Shared QR",qr_image="payment_qr/shared.png",receiver_name="LUCA",upi_id="luca@upi",is_active=True)
        self.client.force_login(self.member)

        response=self.client.get(reverse("payments:member_qr"),{"event":self.event.pk})

        self.assertEqual(response.context["qr"],qr)
        self.assertContains(response,"Shared QR")

    def test_event_specific_qr_is_not_used(self):
        PaymentQRCode.objects.create(event=self.event,title="Old QR",qr_image="payment_qr/old.png",receiver_name="Old",upi_id="old@upi",is_active=True)
        self.client.force_login(self.member)

        response=self.client.get(reverse("payments:member_qr"),{"event":self.event.pk})

        self.assertIsNone(response.context["qr"])
