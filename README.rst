-------------
django-db-log
-------------

Logs Django exceptions to your database handler.

*This project has been replaced by Sentry (https://getsentry.com)*

=========
Upgrading
=========

If you use South migrations, simply run::

	python manage.py migrate djangodblog

If you don't use South, then start.

###############
Notable Changes
###############

* 2.1.0 There is no longer a middleware. Instead, we use a fallback exception handler which catches all.
* 2.0.0 Added `checksum` column to Error. Several indexes were created. Checksum calculation slightly changed.
* 1.4.0 Added `logger` column to both Error and ErrorBatch. `traceback` and `class_name` are now nullable.
* 1.3.0 Added `level` column to both Error and ErrorBatch.

=======
Install
=======

The easiest way to install the package is via pip::

	pip install django-db-log --upgrade

OR, if you're not quite on the same page (work on that), with setuptools::

	easy_install django-db-log

Once installed, update your settings.py and add dblog to ``INSTALLED_APPS``::

	INSTALLED_APPS = (
	    'django.contrib.admin',
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'djangodblog',
	    ...
	)

Finally, run ``python manage.py syncdb`` to create the database tables.

=============
Configuration
=============

Several options exist to configure django-db-log via your ``settings.py``:

######################
DBLOG_CATCH_404_ERRORS
######################

Enable catching of 404 errors in the logs. Default value is ``False``::

	DBLOG_CATCH_404_ERRORS = True

You can skip other custom exception types by adding a ``skip_dblog = True`` attribute to them.

####################
DBLOG_DATABASE_USING
####################

Use a secondary database to store error logs. This is useful if you have several websites and want to aggregate error logs onto one database server::

	# This should correspond to a key in your DATABASES setting
	DBLOG_DATABASE_USING = 'default'

You should also enable the ``DBLogRouter`` to avoid things like extraneous table creation::

	DATABASE_ROUTERS = [
		'djangodblog.routers.DBLogRouter',
		...
	]

Some things to note:

* This functionality REQUIRES Django 1.2.

#########################
DBLOG_ENHANCED_TRACEBACKS
#########################

Enables showing full embedded (enhanced) tracebacks within the administration for "Messages". These work almost identically to the default exception pages within Django's DEBUG environment::

	# Disable embedded interactive tracebacks in the admin
	DBLOG_ENHANCED_TRACEBACKS = False

* Note: Even if you disable displaying of enhanced tracebacks, dblog will still store the entire exception stacktrace.

#############
DBLOG_LOGGING
#############

Enabling this setting will turn off automatic database logging within the exception handler, and instead send all exceptions to the named logger ``dblog``. Use this in conjuction with ``djangodblog.handlers.DBLogHandler`` or your own handler to tweak how logging is dealt with.

A good example use case for this, is if you want to write to something like a syslog ahead of time, and later process that into the database with another tool.

############################
Integration with ``logging``
############################

django-db-log supports the ability to directly tie into the ``logging`` module. To use it simply add ``DBLogHandler`` to your logger::

	import logging
	from djangodblog.handlers import DBLogHandler
	
	logging.getLogger().addHandler(DBLogHandler())

	# Add StreamHandler to dblog's default so you can catch missed exceptions
	logging.getLogger('dblog').addHandler(logging.StreamHandler())

You can also use the ``exc_info`` and ``extra=dict(url=foo)`` arguments on your ``log`` methods. This will store the appropriate information and allow django-db-log to render it based on that information:

	logging.error('There was some crazy error', exc_info=sys.exc_info(), extra={'url': request.build_absolute_uri()})

=====
Usage
=====

You will find two new admin panels in the automatically built Django administration:

* Messages (Error)
* Message summaries (ErrorBatch)

It will store every single error inside of the `Errors` model, and it will store a collective, or summary, of errors inside of `Error batches` (this is more useful for most cases). If you are using this on multiple sites with the same database, the `Errors` table also contains the SITE_ID for which it the error appeared on.

If you wish to access these within your own views and models, you may do so via the standard model API::

	from djangodblog.models import Error, ErrorBatch
	
	# Pull the last 10 unresolved errors.
	ErrorBatch.objects.filter(status=0).order_by('-last_seen')[0:10]

You can also record errors outside of handler if you want::

	from djangodblog.models import Error
	
	try:
		...
	except Exception, exc:
		Error.objects.create_from_exception(exc, [url=None])

If you wish to log normal messages (useful for non-``logging`` integration)::

	from djangodblog.models import Error
	import logging
	
	Error.objects.create_from_text('Error Message'[, level=logging.WARNING, url=None])

Both the ``url`` and ``level`` parameters are optional. ``level`` should be one of the following:

* ``logging.DEBUG``
* ``logging.INFO``
* ``logging.WARNING``
* ``logging.ERROR``
* ``logging.FATAL``

If you have a custom exception class, similar to Http404, or something else you don't want to log,
you can also add ``skip_dblog = True`` to your exception class or instance, and dblog will simply ignore
the error.

=====
Notes
=====

* django-db-log will automatically integrate with django-idmapper.
* django-db-log supports South migrations.
* The fact that the admin shows large quantities of results, even if there aren't, is not a bug. This is an efficiency hack on top of Django.