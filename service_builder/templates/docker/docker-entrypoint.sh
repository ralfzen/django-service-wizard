#!/bin/bash

# It is responsability of the deployment orchestration to execute before
# migrations, collect static files, create default admin user, etc.

gunicorn -b 0.0.0.0:80 {{ name_project }}.wsgi
