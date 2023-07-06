from rest_framework import serializers
from django.utils.duration import duration_iso_string
from django.utils.dateparse import parse_duration


class DurationFieldInISOFormat(serializers.Field):
    def to_representation(self, value):
        return duration_iso_string(value)

    def to_internal_value(self, data):
        return parse_duration(data)
