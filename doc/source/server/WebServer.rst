==========
Web Server
==========

.. highlight:: apache


..   <VirtualHost *:80>
      ServerAdmin nasko.js@gmail.com
      ErrorLog ${APACHE_LOG_DIR}/SmowWeb_error.log
      CustomLog ${APACHE_LOG_DIR}/SmoWeb_access.log combined
      LogLevel info
   
      ServerName platform.sysmoltd.com
      ServerAlias platform.sysmoltd.com
      WSGIScriptAlias / /srv/SmoWeb/Platform/SmoWeb/wsgi.py
      WSGIDaemonProcess platform.sysmoltd.com python-path=/srv/SmoWeb/Platform:/srv/VirtualEnv/SmoWebPlatform/lib/python2.7/site-packages
      WSGIProcessGroup platform.sysmoltd.com
      WSGIApplicationGroup %{GLOBAL}
      <Directory /srv/SmoWeb/Platform/SmoWeb/ >
        <Files wsgi.py>
          Require all granted
        </Files>
      </Directory>
   
      Alias /static/ /srv/SmoWeb/Static/
      <Directory /srv/SmoWeb/Static>
          Require all granted
      </Directory>
   </VirtualHost>