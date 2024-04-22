#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from utils.handler import Handler
from environment import EnviromentBase
from StarDiscord.consumers import ChatConsumer
import threading

def main():
    EnviromentBase.instance().registerFunction(Handler.handlerLogin,"610003")
    EnviromentBase.instance().registerFunction(Handler.handlerChat, "610001")
    EnviromentBase.instance().registerFunction(Handler.msgResponse, "610004")
    t = threading.Thread(target=ChatConsumer.pollEvent, args=(ChatConsumer.sockets, ))
    t.start()
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StarDiscord.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
