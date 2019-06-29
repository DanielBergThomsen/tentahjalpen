"""
File is meant to be executed when in production, using some a WSGI HTTP server such as
gunicorn.
"""

from tentahjalpen import create_app

APP = create_app(production=True)
