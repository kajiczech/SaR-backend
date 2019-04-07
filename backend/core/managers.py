from django.db.models import Manager, QuerySet


class BaseManager(Manager):

    def get_queryset(self):
            qs = super().get_queryset()
            qs = qs.filter(deleted=0)
            return qs

    def with_deleted(self):
        return super().get_queryset()
