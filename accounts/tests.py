from django.test import TestCase
from django.urls import reverse
from promoters.models import PromoterProfile
from .models import User
from .utils import generate_luca_id


class AuthenticationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin-test", password="StrongPass!123", role="ADMIN", luca_id="LUCA-A-0001")
        self.member = User.objects.create_user(username="member-test", password="StrongPass!123", role="MEMBER", luca_id="LUCA-M-0001")

    def test_luca_id_login_and_role_redirect(self):
        response = self.client.post(reverse("accounts:login"), {"identifier": self.member.luca_id, "password": "StrongPass!123"})
        self.assertRedirects(response, reverse("dashboard:redirect"), fetch_redirect_response=False)
        self.assertRedirects(self.client.get(reverse("dashboard:redirect")), reverse("dashboard:member_dashboard"), fetch_redirect_response=False)

    def test_member_cannot_access_admin_os(self):
        self.client.force_login(self.member)
        self.assertRedirects(self.client.get(reverse("events:list")), reverse("dashboard:redirect"), fetch_redirect_response=False)

    def test_disabled_account_is_rejected(self):
        self.member.is_account_active = False
        self.member.save(update_fields=["is_account_active"])
        response = self.client.post(reverse("accounts:login"), {"identifier": self.member.luca_id, "password": "StrongPass!123"})
        self.assertContains(response, "account has been disabled")

    def test_luca_id_generation_uses_latest_number(self):
        User.objects.create_user(username="later", password="x", role="MEMBER", luca_id="LUCA-M-0010")
        self.assertEqual(generate_luca_id(User.Role.MEMBER), "LUCA-M-0011")

    def test_admin_can_remove_member_without_deleting_history_profile(self):
        profile = PromoterProfile.objects.create(user=self.member)
        self.client.force_login(self.admin)

        response = self.client.post(reverse("accounts:member_remove", args=(self.member.pk,)))

        self.assertRedirects(response, reverse("accounts:member_list"))
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_account_active)
        self.assertFalse(self.member.is_active)
        self.assertTrue(PromoterProfile.objects.filter(pk=profile.pk).exists())

    def test_member_remove_confirmation_does_not_change_account(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("accounts:member_remove", args=(self.member.pk,)))

        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_account_active)

    def test_uploaded_profile_photo_is_rendered(self):
        PromoterProfile.objects.create(user=self.member)
        self.member.profile_image="profiles/member-photo.jpg"
        self.member.save(update_fields=["profile_image"])
        self.member.refresh_from_db()
        self.client.force_login(self.member)

        response=self.client.get(reverse("accounts:profile"))

        self.assertContains(response,self.member.profile_image.url)
