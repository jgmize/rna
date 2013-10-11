# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls.defaults import url, patterns, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'channels', views.ChannelViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'notes', views.NoteViewSet)
router.register(r'releases', views.ReleaseViewSet)

urlpatterns = router.urls
