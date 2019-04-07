from unittest import TestCase

from backend.apps.sar.models import Operation
from backend.core.models import BaseModel


class BaseModelTest(TestCase):

    def testDelete(self):
        model = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        assert model.deleted == 0
        model.delete()
        assert model.deleted == 1
        assert Operation.objects.with_deleted().get(id=model.id)
        model.delete(from_db=1)
        self.assertRaises(Operation.DoesNotExist, Operation.objects.with_deleted().get, id=model.id)
