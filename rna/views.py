# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from rest_framework.viewsets import ModelViewSet

from . import models, serializers


def id_set(queryset):
    return set(queryset.values_list('id', flat=True))


class NoteViewSet(ModelViewSet):
    model = models.Note


class ReleaseViewSet(ModelViewSet):
    model = models.Release


class ReleaseNoteViewSet(ModelViewSet):
    model = models.Release
    serializer_class = serializers.ReleaseNoteSerializer

    def update(self, request, *args, **kwargs):
        """
        Store a set of note ids in a pre_update_notes instance
        variable before returning the super method.

        We override the update method instead of pre_save because
        the note_set m2m relation is modified before the pre_save method
        is called.
        """
        obj = self.get_object_or_none()
        self.pre_update_notes = obj and id_set(obj.note_set)
        return super(ReleaseNoteViewSet, self).update(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        """
        Update the modified field of any notes that were added or removed.
        """
        models.Note.objects.filter(
            id__in=id_set(obj.note_set).symmetric_difference(
                self.pre_update_notes)).update(modified=datetime.now())
