import asyncio
import json
import logging
from django.http import HttpResponse
from .bot import sri_lanka_bot


def index(request):
    if request.method == 'POST':
        data = request.body
        res = json.loads(data.decode('utf-8'))
        logging.debug(res)
        asyncio.run(sri_lanka_bot(res))
        return HttpResponse("ok")
    else:
        return HttpResponse("hello world!")
