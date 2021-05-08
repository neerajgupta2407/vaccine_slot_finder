# Create your tests here.
from django.test import TestCase
from model_bakery import baker

from app.models import TelegramAccount


class TestRegistration(TestCase):
    def setUp(self) -> None:
        self.tele = baker.make(TelegramAccount)

    def test_new_register(self):
        tele = TelegramAccount.subscribe("12345", "test user")
        obj = TelegramAccount.objects.get(pk=tele.id)
        self.assertEquals("12345", obj.chat_id)
        self.assertEquals("test user", obj.username)

    def test_register(self):
        pincode = "110027"
        self.assertFalse(self.tele.registered_18)
        self.assertFalse(self.tele.registered_45)
        self.tele.register(pincode, 20)
        self.tele.register(pincode, 45)
        self.tele.refresh_from_db()
        self.assertTrue(self.tele.registered_18)
        self.assertTrue(self.tele.registered_45)
