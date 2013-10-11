# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from django.test import TestCase
from django.test.utils import override_settings
from mock import Mock, patch
from nose.tools import eq_, ok_

from . import clients, fields, filters, models 


class TimeStampedModelTest(TestCase):
    @patch('rna.rna.models.models.Model.save')
    def test_default_modified(self, mock_super_save):
        start = datetime.now()
        model = models.TimeStampedModel()
        model.save(db='test')
        ok_(model.modified > start)
        mock_super_save.assert_called_once_with(db='test')

    @patch('rna.rna.models.models.Model.save')
    def test_unmodified(self, mock_super_save):
        model = models.TimeStampedModel()
        model.modified = space_odyssey = datetime(2001, 1, 1)
        model.save(modified=False, db='test')
        eq_(model.modified, space_odyssey)
        mock_super_save.assert_called_once_with(db='test')


class ChannelTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        channel = models.Channel(name='test')
        eq_(unicode(channel), 'test')


class ProductTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        product = models.Product(name='test')
        eq_(unicode(product), 'test')


class NoteTest(TestCase):
    def test_unicode(self):
        """
        Should equal description
        """
        note = models.Note(html='test')
        eq_(unicode(note), 'test')

    def test_markdown_to_html(self):
        """
        Should convert markdown to html
        """
        note = models.Note(markdown='test')
        expected_html = '<p>test</p>'
        self.assertTrue(note.markdown_to_html(), expected_html)
        eq_(note.html, expected_html)

    def test_markdown_to_html_no_markdown(self):
        """
        Should not override html
        """
        note = models.Note(html='test')
        eq_(note.markdown_to_html(), None)
        eq_(note.html, 'test')

    @patch('rna.rna.models.Note.markdown_to_html')
    @patch('django.db.models.Model.save')
    def test_save(self, mock_super_save, mock_markdown_to_html):
        """
        Should call markdown_to_html and super save
        """
        note = models.Note()
        note.save('test_arg', test_kwarg='test')
        mock_markdown_to_html.assert_called_once()
        mock_super_save.assert_called_with('test_arg', test_kwarg='test')
        
        

class TagTest(TestCase):
    def test_unicode(self):
        """
        Should equal text
        """
        tag = models.Tag(text='test')
        eq_(unicode(tag), 'test')


class ReleaseTest(TestCase):
    def test_unicode(self):
        """
        Should equal text
        """
        release = models.Release(text='test')
        eq_(unicode(release), 'test')


class ISO8601DateTimeFieldTest(TestCase):
    @patch('rna.rna.fields.parse_datetime')
    def test_strptime(self, mock_parse_datetime):
        """
        Should equal expected_date returned by mock_parse_datetime
        """
        expected_date = datetime(2001, 1, 1)
        mock_parse_datetime.return_value = expected_date
        field = fields.ISO8601DateTimeField()
        eq_(field.strptime('value', 'format'), expected_date)


class TimeStampedModelSubclass(models.TimeStampedModel):
    test = models.models.BooleanField(default=True)


class TimestampedFilterBackendTest(TestCase):
    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_filter_class(self, mock_super_get_filter_class):
        """
        Should return super call if view has filter_class attr
        """
        mock_super_get_filter_class.return_value = 'The Dude'
        mock_view = Mock(filter_class='abides')
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(mock_view), 'The Dude')

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_filter_fields(self, mock_super_get_filter_class):
        """
        Should return super call if view has filter_fields attr
        """
        mock_super_get_filter_class.return_value = 'The Dude'
        mock_view = Mock(filter_fields='abides')
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(mock_view), 'The Dude')

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_no_queryset(self, mock_super_get_filter_class):
        """
        Should return None if queryset is None (the default)
        """
        view = 'nice'
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(view), None)
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_non_timestampedmodel(self, mock_super_get_filter_class):
        """
        Should return None if queryset.model is not a subclass of
        models.TimeStampedModel
        """
        view = 'nice'
        queryset = Mock(model=models.models.Model)  # model
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(view, queryset=queryset), None)
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_default(self, mock_super_get_filter_class):
        """
        Should return a subclass of the default_filter_set instance
        attr with the inner Meta class model attr equal to the queryset
        model and fields equal to all of the model fields except
        created and modified, and in addition the created_before,
        created_after, modified_before, and modified_after fields 
        """
        view = 'nice'
        queryset = Mock(model=TimeStampedModelSubclass)
        filter_backend = filters.TimestampedFilterBackend()
        filter_class = filter_backend.get_filter_class(view, queryset=queryset)
        eq_(filter_class.Meta.model, TimeStampedModelSubclass)
        eq_(filter_class.Meta.fields,
            ['created_before', 'created_after', 'modified_before',
             'modified_after', 'id', 'test'])
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_exclude_fields(self, mock_super_get_filter_class):
        """
        Should not include fields named in the view.
        """
        view = lambda: None
        view.filter_fields_exclude = ('created_before', 'id')
        queryset = Mock(model=TimeStampedModelSubclass)
        filter_backend = filters.TimestampedFilterBackend()
        filter_class = filter_backend.get_filter_class(view, queryset=queryset)
        eq_(filter_class.Meta.model, TimeStampedModelSubclass)
        eq_(filter_class.Meta.fields,
            ['created_after', 'modified_before', 'modified_after', 'test'])
        ok_(not mock_super_get_filter_class.called)


class RestClientTest(TestCase):
    def test_init_kwargs(self):
        """
        Should set base_url and token attr from kwargs
        """
        rc = clients.RestClient(base_url='http://thedu.de', token='midnight')
        eq_(rc.base_url, 'http://thedu.de')
        eq_(rc.token, 'midnight')

    @override_settings(RNA_AUTH_TOKEN='midnight',
                       RNA_REMOTE_BASE_URL='http://thedu.de')
    def test_init_settings(self):
        """
        Should set base_url and token attr from settings
        """
        rc = clients.RestClient()
        eq_(rc.base_url, 'http://thedu.de')
        eq_(rc.token, 'midnight')

    @patch('rna.rna.clients.requests.request')
    def test_request_base_url_concat(self, mock_request):
        """
        Should concatenate base_url and url and load json by default
        """

        rc = clients.RestClient(base_url='http://thedu.de')
        mock_request.return_value = Mock(content='{"aggression": "not stand"}')
        response = rc.request('get', '/abides')
        mock_request.assert_called_once_with('get', 'http://thedu.de/abides')
        eq_(response, {'aggression': 'not stand'})

    @patch('rna.rna.clients.requests.request')
    def test_request_redundant_url(self, mock_request):
        """
        Should not concatenate base_url if url starts with it
        """

        rc = clients.RestClient(base_url='http://thedu.de')
        mock_request.return_value = Mock(content='{"aggression": "not stand"}')
        response = rc.request('get', 'http://thedu.de/abides')
        mock_request.assert_called_once_with('get', 'http://thedu.de/abides')

    @patch('rna.rna.clients.requests.request')
    def test_request_token(self, mock_request):
        """
        Should set Authorization header to expected format
        """
        rc = clients.RestClient(base_url='http://thedu.de', token='midnight')
        mock_request.return_value = Mock(content='{"aggression": "not stand"}')
        response = rc.request('get', '')
        mock_request.assert_called_once_with(
            'get', 'http://thedu.de',
            headers={'Authorization': 'Token midnight'})
        eq_(response, {'aggression': 'not stand'})

    @patch('rna.rna.clients.requests.request')
    def test_request_token_preserves_headers(self, mock_request):
        """
        Should set Authorization header to expected format without removing
        other headers
        """
        rc = clients.RestClient(base_url='http://thedu.de', token='midnight')
        mock_request.return_value = Mock(content='{"aggression": "not stand"}')
        response = rc.request('get', '', headers={'White': 'Russian'})
        mock_request.assert_called_once_with(
            'get', 'http://thedu.de',
            headers={'Authorization': 'Token midnight', 'White': 'Russian'})
        eq_(response, {'aggression': 'not stand'})

    @patch('rna.rna.clients.requests.request')
    def test_request_load_json_false(self, mock_request):
        """
        Should return unmodified response from requests.request
        """
        rc = clients.RestClient(base_url='http://thedu.de')
        mock_request.return_value = Mock(content='abides', status_code=200)
        response = rc.request('get', '', load_json=False)
        mock_request.assert_called_once_with('get', 'http://thedu.de')
        eq_(response.content, 'abides')
        eq_(response.status_code, 200)

    @patch('rna.rna.clients.requests.request')
    def test_request_delete(self, mock_request):
        """
        Should return unmodified response from requests.request
        """
        rc = clients.RestClient(base_url='http://th.is')
        mock_request.return_value = Mock(status_code=204)
        response = rc.request('delete', '/aggression')
        mock_request.assert_called_once_with(
            'delete', 'http://th.is/aggression')
        eq_(response.status_code, 204) 

    @patch('rna.rna.clients.RestClient.request')
    def test_delete(self, mock_request):
        """
        Should pass through kwargs and return unmodified response from
        self.request
        """
        rc = clients.RestClient(base_url='http://th.is')
        mock_request.return_value = Mock(status_code=204)
        response = rc.delete('/aggression', params={'will': 'not stand'})
        mock_request.assert_called_once_with(
            'delete', '/aggression', params={'will': 'not stand'})
        eq_(response.status_code, 204) 

    @patch('rna.rna.clients.RestClient.request')
    def test_get(self, mock_request):
        """
        Should pass through kwargs and return unmodified response from
        self.request
        """
        rc = clients.RestClient(base_url='http://thedu.de')
        mock_request.return_value = Mock(content='abides')
        response = rc.get('', params={'white': 'russian'})
        mock_request.assert_called_once_with(
            'get', '', params={'white': 'russian'})
        eq_(response.content, 'abides')

    @patch('rna.rna.clients.RestClient.request')
    def test_options(self, mock_request):
        """
        Should pass through kwargs and return unmodified response from
        self.request
        """
        rc = clients.RestClient(base_url='http://thedu.de')
        mock_request.return_value = {'white': 'russians'}
        response = rc.options('/drinks')
        mock_request.assert_called_once_with('options', '/drinks')
        eq_(response, {'white': 'russians'})

    @patch('rna.rna.clients.RestClient.request')
    def test_post(self, mock_request):
        """
        Should pass through data to, and return unmodified response
        from, self.request
        """
        rc = clients.RestClient(base_url='http://walt.er')
        mock_request.return_value = Mock(
            content='Is this your homework, Larry?')
        response = rc.post('/larry', data={'world': 'of pain'})
        mock_request.assert_called_once_with(
            'post', '/larry', data={'world': 'of pain'})
        eq_(response.content, 'Is this your homework, Larry?')

    @patch('rna.rna.clients.RestClient.request')
    def test_put(self, mock_request):
        """
        Should pass through data to, and return unmodified response
        from, self.request
        """
        rc = clients.RestClient(base_url='http://walt.er')
        mock_request.return_value = Mock(
            content='Is this your homework, Larry?')
        response = rc.put('/larry', data={'world': 'of pain'})
        mock_request.assert_called_once_with(
            'put', '/larry', data={'world': 'of pain'})
        eq_(response.content, 'Is this your homework, Larry?')

