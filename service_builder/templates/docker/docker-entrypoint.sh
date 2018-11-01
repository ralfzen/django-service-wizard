#!/bin/bash

# It is responsability of the deployment orchestration to execute before
# migrations, create default admin user, populate minimal data, etc.

gunicorn {{ name_project }}.wsgi --config {{ name_project }}/gunicorn_conf.py
