# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.db import models
from django.conf import settings

from django_extensions.db.fields import CreationDateTimeField

class TimeStampedModel(models.Model):
    """
    Replacement for django_extensions.db.models.TimeStampedModel
    that updates the modified timestamp by default, but allows
    that behavior to be overridden by passing a modified=False
    parameter to the save method
    """
    created = CreationDateTimeField()
    modified = models.DateTimeField(editable=False, blank=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if kwargs.pop('modified', True):
            self.modified = datetime.now() 
        super(TimeStampedModel, self).save(*args, **kwargs)


class Channel(models.Model):
    name = models.TextField(unique=True, db_column='channel_name')

    class Meta:
        db_table = u'Channels'

    def __unicode__(self):
        return self.name


class Product(models.Model):
    name = models.TextField(unique=True, db_column='product_name')
    text = models.TextField(blank=True, db_column='product_text')

    class Meta:
        db_table = u'Products'

    def __unicode__(self):
        return self.name


class Note(models.Model):
    bug_num = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    first_version = models.IntegerField(null=True, blank=True)
    first_channel = models.ForeignKey(Channel, null=True, db_column='first_channel', blank=True, related_name='first_channel_notes')
    fixed_in_version = models.IntegerField(null=True, blank=True)
    fixed_in_channel = models.ForeignKey(Channel, null=True, db_column='fixed_in_channel', blank=True, related_name='fixed_in_channel_notes')
    tag = models.IntegerField(null=True, blank=True)
    product = models.ForeignKey(Product, null=True, db_column='product', blank=True)
    sort_num = models.IntegerField(null=True, blank=True)
    fixed_in_subversion = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('sort_num',)
        db_table = u'Notes'

    def __unicode__(self):
        return self.description


class Tag(models.Model):
    text = models.TextField(db_column='tag_text')
    sort_num = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('sort_num',)
        db_table = u'Tags'

    def __unicode__(self):
        return self.text


class Release(models.Model):
    product = models.ForeignKey(Product, db_column='product')
    channel = models.ForeignKey(Channel, db_column='channel')
    version = models.IntegerField()
    sub_version = models.IntegerField()
    release_date = models.DateTimeField()
    text = models.TextField(blank=True, db_column='release_text')

    class Meta:
        db_table = u'Releases'

    def __unicode__(self):
        return self.text
