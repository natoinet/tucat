#!/usr/bin/env python
import os
import sys
import environ

if __name__ == "__main__":
    # Read .env file, in order to set DJANGO_SETTINGS_MODULE
    environ.Env().read_env()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
