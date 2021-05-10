# Create your tests here.
from django.test import TestCase
from model_bakery import baker

from app.models import *


class TestRegistration(TestCase):
    def setUp(self) -> None:
        self.tele = baker.make(TelegramAccount)
        self.district = baker.make(Disrtict)

    def test_new_register(self):
        tele = TelegramAccount.subscribe("12345", "test user")
        obj = TelegramAccount.objects.get(pk=tele.id)
        self.assertEquals("12345", obj.chat_id)
        self.assertEquals("test user", obj.username)

    def test_register_pincode(self):
        pincode = "110027"
        self.assertFalse(self.tele.registered_18)
        self.assertFalse(self.tele.registered_45)
        self.tele.alert(AgeType._forty_five, pincode=pincode)
        self.tele.alert(AgeType._eighteen, pincode=pincode)
        self.tele.refresh_from_db()
        self.assertTrue(len(self.tele.saved_alerts) == 2)
        saved_alerts = self.tele.saved_alerts
        self.assertEquals(saved_alerts[AgeType._forty_five]["pincodes"], [pincode])

    def test_register_district(self):
        pincode = "110027"
        pincode2 = "110028"
        self.assertFalse(self.tele.registered_18)
        self.assertFalse(self.tele.registered_45)
        self.tele.alert(
            AgeType._forty_five, district_id=self.district.pk, pincode=pincode
        )
        self.tele.alert(
            AgeType._eighteen, district_id=self.district.pk, pincode=pincode
        )
        self.tele.refresh_from_db()
        self.assertTrue(len(self.tele.saved_alerts) == 2)
        saved_alerts = self.tele.saved_alerts
        self.assertEquals(
            saved_alerts[AgeType._forty_five]["district_ids"], [self.district.pk]
        )
        self.assertEquals(saved_alerts[AgeType._forty_five]["pincodes"], [pincode])

        self.tele.alert(AgeType._eighteen, pincode=pincode2)
        self.tele.refresh_from_db()
        expected_lis = [pincode, pincode2]
        expected_lis.sort()
        saved_alerts[AgeType._eighteen]["pincodes"].sort()
        self.assertListEqual(
            [pincode, pincode2], saved_alerts[AgeType._eighteen]["pincodes"]
        )

    def test_save_recent_seartches(self):
        q1 = "query1"
        q2 = "query2"
        q3 = "query3"
        q4 = "query4"
        self.tele.save_search_query(q1)
        self.tele.save_search_query(q2)
        self.tele.save_search_query(q3)
        self.tele.save_search_query(q4)
        self.tele.refresh_from_db()
        recent_searches = self.tele.get_recent_searches(2)
        self.assertEquals(4, len(self.tele.recent_searches))
        self.assertListEqual([q4, q3], recent_searches)

    def test_subscribed_data(self):
        tele1 = baker.make(TelegramAccount)
        tele2 = baker.make(TelegramAccount)
        tele3 = baker.make(TelegramAccount)
        d1 = baker.make(Disrtict)
        d2 = baker.make(Disrtict)
        d3 = baker.make(Disrtict)
        pincode1 = "110027"
        pincode2 = "110028"
        pincode3 = "110029"
        tele1.alert(AgeType._eighteen, pincode=pincode1, district_id=d1.pk)
        tele2.alert(AgeType._forty_five, pincode=pincode2, district_id=d2.pk)
        tele3.alert(AgeType._eighteen, pincode=pincode3)
        data = TelegramAccount.subscribed_data()
        expected_pincodes = ["110027", "110028", "110029"]
        expected_d_ids = [d1.pk, d2.pk]
        expected_pincodes.sort()
        expected_d_ids.sort()
        data["district_ids"].sort()
        data["pincodes"].sort()

        self.assertListEqual(expected_pincodes, data["pincodes"])
        self.assertListEqual(expected_d_ids, data["district_ids"])

        # breakpoint()
        # a = TelegramAccount.objects.all()
        # print([x.saved_alerts for x in a])
        # query = TelegramAccount.objects.filter(saved_alerts__18__pincodes__contains=['110027'])
        # print(query.query)
