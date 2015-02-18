==============
Task scheduler
==============

From `here <http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html#daemonizing>`_

Example configuration
~~~~~~~~~~~~~~~~~~~~~

This is an example configuration for a Python project.

:file:`/etc/default/celeryd`:

.. code-block:: bash

    # Names of nodes to start
    #   most will only start one node:
    CELERYD_NODES="worker1"
    #   but you can also start multiple and configure settings
    #   for each in CELERYD_OPTS (see `celery multi --help` for examples).
    CELERYD_NODES="worker1 worker2 worker3"

    # Absolute or relative path to the 'celery' command:
    CELERY_BIN="/usr/local/bin/celery"
    #CELERY_BIN="/virtualenvs/def/bin/celery"

    # App instance to use
    # comment out this line if you don't use an app
    CELERY_APP="proj"
    # or fully qualified:
    #CELERY_APP="proj.tasks:app"

    # Where to chdir at start.
    CELERYD_CHDIR="/opt/Myproject/"

    # Extra command-line arguments to the worker
    CELERYD_OPTS="--time-limit=300 --concurrency=8"

    # %N will be replaced with the first part of the nodename.
    CELERYD_LOG_FILE="/var/log/celery/%N.log"
    CELERYD_PID_FILE="/var/run/celery/%N.pid"

    # Workers should run as an unprivileged user.
    #   You need to create this user manually (or you can choose
    #   a user/group combination that already exists, e.g. nobody).
    CELERYD_USER="celery"
    CELERYD_GROUP="celery"

    # If enabled pid and log directories will be created if missing,
    # and owned by the userid/group configured.
    CELERY_CREATE_DIRS=1

.. _generic-initd-celeryd-django-example:

Example Django configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django users now uses the exact same template as above,
but make sure that the module that defines your Celery app instance
also sets a default value for :envvar:`DJANGO_SETTINGS_MODULE`
as shown in the example Django project `here <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#django-first-steps>`_.

.. _generic-initd-celeryd-options:

Available options
~~~~~~~~~~~~~~~~~

* CELERY_APP
    App instance to use (value for ``--app`` argument).
    If you're still using the old API, or django-celery, then you
    can omit this setting.

* CELERY_BIN
    Absolute or relative path to the :program:`celery` program.
    Examples:

        * :file:`celery`
        * :file:`/usr/local/bin/celery`
        * :file:`/virtualenvs/proj/bin/celery`
        * :file:`/virtualenvs/proj/bin/python -m celery`

* CELERYD_NODES
    List of node names to start (separated by space).

* CELERYD_OPTS
    Additional command-line arguments for the worker, see
    `celery worker --help` for a list.  This also supports the extended
    syntax used by `multi` to configure settings for individual nodes.
    See `celery multi --help` for some multi-node configuration examples.

* CELERYD_CHDIR
    Path to change directory to at start. Default is to stay in the current
    directory.

* CELERYD_PID_FILE
    Full path to the PID file. Default is /var/run/celery/%N.pid

* CELERYD_LOG_FILE
    Full path to the worker log file. Default is /var/log/celery/%N.log

* CELERYD_LOG_LEVEL
    Worker log level. Default is INFO.

* CELERYD_USER
    User to run the worker as. Default is current user.

* CELERYD_GROUP
    Group to run worker as. Default is current user.

* CELERY_CREATE_DIRS
    Always create directories (log directory and pid file directory).
    Default is to only create directories when no custom logfile/pidfile set.

* CELERY_CREATE_RUNDIR
    Always create pidfile directory.  By default only enabled when no custom
    pidfile location set.

* CELERY_CREATE_LOGDIR
    Always create logfile directory.  By default only enable when no custom
    logfile location set.
