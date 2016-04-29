from django.utils import timezone
from rest_framework import serializers


class DateTimeTzAwareField(serializers.DateTimeField):

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeTzAwareField, self).to_representation(value)
