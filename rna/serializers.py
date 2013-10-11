from django.db import models
from rest_framework import serializers
from rest_framework.compat import parse_datetime

from . import fields

def get_client_serializer_class(model_class):
    class ClientSerializer(UnmodifiedTimestampSerializer):
        class Meta:
            model = model_class

    return ClientSerializer


class HyperlinkedModelSerializerWithPkField(
        serializers.HyperlinkedModelSerializer):

    def get_pk_field(self, model_field):
        """
        Returns a default instance of the pk fiel.
        """
        return self.get_field(model_field)


class UnmodifiedTimestampSerializer(serializers.ModelSerializer):
    def restore_object(self, attrs, instance=None):
        obj = super(UnmodifiedTimestampSerializer, self).restore_object(
            attrs, instance=instance)
        for attr in ('created', 'modified'):  #TODO: dynamic attr list
            value = getattr(obj, attr, None)
            if value and isinstance(value, basestring):
                setattr(obj, attr, parse_datetime(value))
        return obj

    def save_object(self, obj, **kwargs):
        kwargs['modified'] = False
        return super(UnmodifiedTimestampSerializer, self).save_object(
            obj, **kwargs)
