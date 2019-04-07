from unittest import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.contrib.auth.models import User

from backend.apps.sar.models import *
from backend.core.api.GenericViewSet import GenericViewSet
from rest_framework.test import APITestCase
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from oauth2_provider.models import get_application_model
from oauth2_provider.models import get_access_token_model
from decimal import *


Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()


class BaseManagerTest(TestCase):

    def testDeleteRetrieve(self):
        model = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        model.delete()
        assert model.deleted == 1
        self.assertRaises(Operation.DoesNotExist, Operation.objects.get, id=model.id)
        operation = Operation.objects.with_deleted().get(id=model.id)
        assert operation.deleted == 1
        operation.delete(from_db=True)


    def testFilterDelete(self):
        model = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        set = Operation.objects.filter(name="FirstOperation").exclude(type="bambi")
        assert set.count() == 1
        model.delete()
        set = Operation.objects.filter(name="FirstOperation")
        assert set.count() == 0
        set = Operation.objects.filter(name="FirstOperation")
        assert set.count() == 0
        set = Operation.objects.with_deleted().all()
        assert set.count() == 1
        self.assertRaises(Operation.DoesNotExist, Operation.objects.get, id=model.id)
        operation = Operation.objects.with_deleted().get(id=model.id)
        assert operation.deleted == 1
        self.assertRaises(Operation.DoesNotExist, Operation.objects.get, id=model.id, deleted=1)
        operation.delete(from_db=True)




