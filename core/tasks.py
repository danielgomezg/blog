from __future__ import absolute_import, unicode_literals

from celery import shared_task

import logging #se usa logging en vez de print

logger = logging.getLogger(__name__)

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings") #igual que en celery.py
django.setup() #para poder usar las apps de django como blog

@shared_task
def test_task():
    logger.info("Test celery")