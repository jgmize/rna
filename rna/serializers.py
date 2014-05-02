# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import serializers
from rest_framework.compat import parse_datetime

from .models import Release


def get_client_serializer_class(model_class):
    class ClientSerializer(UnmodifiedTimestampSerializer):
        class Meta:
            model = model_class

    return ClientSerializer


class HyperlinkedModelSerializerWithPkField(
        serializers.HyperlinkedModelSerializer):

    def get_pk_field(self, model_field):
        """
        Returns a default instance of the pk field, unlike
        the parent class, which omits the pk field.
        """
        return self.get_field(model_field)


class ReleaseNoteSerializer(HyperlinkedModelSerializerWithPkField):
    class Meta:
        model = Release
        fields = [f.name for f in Release._meta.fields] + ['note_set']


class UnmodifiedTimestampSerializer(serializers.ModelSerializer):
    def restore_object(self, attrs, instance=None):
        obj = super(UnmodifiedTimestampSerializer, self).restore_object(
            attrs, instance=instance)
        for attr in ('created', 'modified'):  # TODO: dynamic attr list
            value = getattr(obj, attr, None)
            if value and isinstance(value, basestring):
                setattr(obj, attr, parse_datetime(value))
        return obj

    def save_object(self, obj, **kwargs):
        kwargs['modified'] = False
        return super(UnmodifiedTimestampSerializer, self).save_object(
            obj, **kwargs)
