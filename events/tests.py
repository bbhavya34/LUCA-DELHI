from django.test import TestCase

from .forms import EventForm, EventPhotoForm
from .models import Event


class EventVisibilityTests(TestCase):
    def test_gallery_selector_includes_event_regardless_of_status(self):
        event=Event.objects.create(name="New event",event_date="2026-08-01",start_time="20:00",status=Event.Status.DRAFT)

        self.assertIn(event,EventPhotoForm().fields["event"].queryset)


class EventCreationFormTests(TestCase):
    def test_form_only_shows_start_time(self):
        form=EventForm()

        self.assertIn("start_time",form.fields)
        self.assertNotIn("end_time",form.fields)
