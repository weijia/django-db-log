from django.conf import settings
from django.conf.urls.defaults import *
# from django.utils.hashcompat import md5_constructor
from django.conf.urls import patterns, url
try:
    import hashlib
    md5_constructor = hashlib.md5
except ImportError:
    import md5
    md5_constructor = md5.new

from feeds import ErrorFeed, SummaryFeed

hashed_secret = md5_constructor(settings.SECRET_KEY).hexdigest()

urlpatterns = patterns('',
    url(r'feeds/%s/messages.xml' % hashed_secret, ErrorFeed(), name='dblog-feed-messages'),
    url(r'feeds/%s/summaries.xml' % hashed_secret, SummaryFeed(), name='dblog-feed-summaries'),
)
