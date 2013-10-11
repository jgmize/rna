# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

from django.conf import settings
import requests

from . import models, serializers


class RestClient(object):

    def __init__(self, base_url='', token=''):
        """Initialize the RestClient based on the provided
        base_url and token, if provided.

        Args:
            base_url (str): The full URL which all requests will
                be relative to. Defaults to settings.RNA_REMOTE_BASE_URL
            token (str): Token to add to Authorization HTTP header.
                Defaults to settings.RNA_AUTH_TOKEN
        """
        self.base_url = base_url or settings.RNA_REMOTE_BASE_URL
        self.token = token or getattr(settings, 'RNA_AUTH_TOKEN', '')

    def request(self, method, url, **kwargs):
        if self.base_url and not url.startswith(self.base_url):
            url = self.base_url + url
        if self.token:
            kwargs.setdefault('headers', {})
            kwargs['headers'].setdefault(
                'Authorization', 'Token ' + self.token)
        load_json = kwargs.pop('load_json', not method == 'delete')
        # No error handling here; may want to change that later.
        response = requests.request(method, url, **kwargs)
        if load_json:
            return json.loads(response.content)
        else:
            return response

    def delete(self, url='', **kwargs):
        return self.request('delete', url, **kwargs)

    def get(self, url='', **kwargs):
        return self.request('get', url, **kwargs)

    def options(self, url='', **kwargs):
        return self.request('options', url, **kwargs)

    def post(self, url='', data=None, **kwargs):
        return self.request('post', url, data=data, **kwargs)

    def put(self, url='', data=None, **kwargs):
        return self.request('put', url, data=data, **kwargs)


class RestModelClient(RestClient):
    def __init__(self, base_url='', token='', **kwargs):
        self.Model = kwargs.pop('model_class', None)
        super(RestModelClient, self).__init__(base_url=base_url, token=token,
                                              **kwargs)

    def get(self, **kwargs):
        model = kwargs.pop('model', False)
        model_class = kwargs.pop('model_class', None)
        save = kwargs.pop('save', False)
        data = super(RestModelClient, self).get(**kwargs)
        if model:
            if isinstance(data, list):
                return [self.model(d, save=save, model_class=model_class)
                        for d in data]
            else:
                return self.model(data, save=save, model_class=model_class)
        else:
            return data

    def model(self, data, save=False, **kwargs):
        serializer = self.serializer(**kwargs)
        data = data.copy()  # prevent the next line from modifying the cache
        data.pop('url', None)
        instance = serializer.restore_object(data)
        if save:
            serializer.save_object(instance)
        return instance

    def models(self, save=False, **kwargs):
        return [self.model(data, save=save) for data in self.get(**kwargs)]
        
    def post(self, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            kwargs['data'] = self.serialize(instance)
        return super(RestModelClient, self).post(**kwargs)

    def put(self, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            kwargs['data'] = self.serialize(instance)
        return super(RestModelClient, self).put(**kwargs)

    def serialize(self, instance):
        return self.serializer(instance=instance).data

    def serializer(self, **kwargs):
        model_class = kwargs.pop('model_class', None) or self.Model
        return serializers.get_client_serializer_class(model_class)(**kwargs)


class DictLikeRestClient(RestClient):
    def __getitem__(self, name):
        return self.get()[name]

    def __setitem__(self, name, value):
        # may want to implement this in a subclass
        raise NotImplementedError

    def __iter__(self):
        return self.get().__iter__()
        
    def __repr__(self):
        return self.get().__repr__()

    def items(self):
        return [(name, self[name]) for name in self]

    def iteritems(self):
        return ((name, self[name]) for name in self)


class CachingRestClient(RestClient):
    def __init__(self, base_url='', token='', **kwargs):
        self.cache = kwargs.pop('cache', {})
        super(CachingRestClient, self).__init__(
            base_url=base_url, token=token, **kwargs)

    def delete(self, url='', **kwargs):
        self.cache.pop(url, None)
        return super(CachingRestClient, self).delete(
            url=url, **kwargs)

    def get(self, url='', **kwargs):
        if kwargs.get('params', None):
            # for now, any params will skip the cache
            return super(CachingRestClient, self).get(url=url, **kwargs)
        if url not in self.cache:
            self.cache[url] = super(CachingRestClient, self).get(
                url=url, **kwargs)
        return self.cache[url] 

    def put(self, url='', data=None, **kwargs):
        self.cache.pop(url, None)
        return super(CachingRestClient, self).put(
            url=url, data=data, **kwargs)

    def post(self, url='', data=None, **kwargs):
        self.cache.pop(url, None)
        return super(CachingRestClient, self).post(
            url=url, data=data, **kwargs)

    def options(self, url='', **kwargs):
        self.cache.setdefault('OPTIONS', {})
        if url not in self.cache['OPTIONS']:
            self.cache['OPTIONS'][url] = super(
                CachingRestClient, self).options(url=url, **kwargs)
        return self.cache['OPTIONS'][url]


class CachingRestModelClient(RestModelClient, CachingRestClient):
    pass


class CachingDictLikeRestClient(CachingRestClient, DictLikeRestClient):
    pass


class RecursiveRestClient(CachingDictLikeRestClient):
    def __getitem__(self, name):
        item = super(RecursiveRestClient, self).__getitem__(name)

        if isinstance(item, basestring) and item.startswith('http') and (
                name != 'url'):
            return self.__class__(item, token=self.token)

        elif isinstance(item, dict) and 'url' in item:
            return self.__class__(item['url'], token=self.token,
                                  cache={'': item})

        elif isinstance(item, list) and isinstance(item[0], dict) and (
                'url' in item[0]):
            return [self.__class__(i['url'], token=self.token, cache={'': i})
                    for i in item]
        return item


class ModelMapClient(RecursiveRestClient, CachingRestModelClient):
    model_map = {}

    def __getitem__(self, name):
        item = super(ModelMapClient, self).__getitem__(name)
        model_class = self.model_map.get(name, None) or getattr(
            self, 'Model', None)
        if model_class and isinstance(item, self.__class__):
            return self.__class__(model_class=model_class,
                                  base_url=item.base_url,
                                  token=item.token, cache=item.cache)
        return item


class RNAModelMapClient(ModelMapClient):
    model_map = {
        'channels': models.Channel,
        'notes': models.Note,
        'products': models.Product,
        'releases': models.Release,
        'tags': models.Tag}
