from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from events.models import Event
from guestlists.models import GuestEntry
from .models import CommissionSettlement,PromoterProfile
from .services import calculate_outstanding_commission


class RemovePromoterTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="password", role=User.Role.ADMIN)
        self.member = User.objects.create_user(
            username="member", password="password", role=User.Role.MEMBER,
            luca_id="MEM001", is_account_active=True,
        )
        self.profile = PromoterProfile.objects.create(user=self.member)
        self.event = Event.objects.create(name="Test event", event_date=date.today(), start_time=time(20, 0))
        self.profile.assigned_events.add(self.event)
        self.client.force_login(self.admin)

    def test_remove_promoter_disables_account_and_clears_assignments(self):
        response = self.client.post(reverse("promoters:remove", args=(self.profile.pk,)))

        self.assertRedirects(response, reverse("promoters:list"))
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_account_active)
        self.assertFalse(self.member.is_active)
        self.assertFalse(self.profile.assigned_events.exists())
        self.assertTrue(PromoterProfile.objects.filter(pk=self.profile.pk).exists())

    def test_remove_promoter_requires_post_to_change_account(self):
        response = self.client.get(reverse("promoters:remove", args=(self.profile.pk,)))

        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_account_active)


class CommissionSettlementTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create_user(username="settlement-admin",password="password",role=User.Role.ADMIN)
        self.member=User.objects.create_user(username="settlement-member",password="password",role=User.Role.MEMBER,luca_id="MEM002")
        self.profile=PromoterProfile.objects.create(user=self.member,commission_type=PromoterProfile.CommissionType.FIXED,commission_value=25)
        GuestEntry.objects.create(promoter=self.member,verification_status=GuestEntry.VerificationStatus.VERIFIED)
        GuestEntry.objects.create(promoter=self.member,verification_status=GuestEntry.VerificationStatus.VERIFIED)
        self.client.force_login(self.admin)

    def test_settle_up_resets_outstanding_and_preserves_ledger(self):
        self.assertEqual(calculate_outstanding_commission(self.member),50)

        response=self.client.post(reverse("promoters:settle_commission",args=(self.profile.pk,)))

        self.assertRedirects(response,reverse("promoters:detail",args=(self.profile.pk,)))
        settlement=CommissionSettlement.objects.get(promoter=self.member)
        self.assertEqual(settlement.amount,50)
        self.assertEqual(settlement.settled_by,self.admin)
        self.assertEqual(calculate_outstanding_commission(self.member),0)

    def test_new_commission_accumulates_after_settlement(self):
        self.client.post(reverse("promoters:settle_commission",args=(self.profile.pk,)))
        GuestEntry.objects.create(promoter=self.member,verification_status=GuestEntry.VerificationStatus.VERIFIED)

        self.assertEqual(calculate_outstanding_commission(self.member),25)

    def test_settlement_requires_post(self):
        response=self.client.get(reverse("promoters:settle_commission",args=(self.profile.pk,)))

        self.assertEqual(response.status_code,405)
        self.assertFalse(CommissionSettlement.objects.exists())
