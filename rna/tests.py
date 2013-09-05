# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from . import models


class ChannelTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        channel = models.Channel(name='test')
        self.assertEqual(unicode(channel), 'test')


class ProductTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        product = models.Product(name='test')
        self.assertEqual(unicode(product), 'test')


class NoteTest(TestCase):
    def test_unicode(self):
        """
        Should equal description
        """
        note = models.Note(description='test')
        self.assertEqual(unicode(note), 'test')


class TagTest(TestCase):
    def test_unicode(self):
        """
        Should equal text
        """
        tag = models.Tag(text='test')
        self.assertEqual(unicode(tag), 'test')


class ReleaseTest(TestCase):
    def test_unicode(self):
        """
        Should equal text
        """
        release = models.Release(text='test')
        self.assertEqual(unicode(release), 'test')
