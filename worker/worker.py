# -*- coding: utf-8 -*-
import threading
from hue import Clipv2
from threading import Thread
from queue import Queue
from .response import Response

class Worker(Thread):
    """
    Update worker that handles all communication with the Hue API
    """
    def __init__(self, request_queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=args, kwargs=kwargs)
        self.hue = Clipv2()
        self.response_queue = Queue()
        self.request_queue = request_queue

    def run(self):
        while True:
            request = self.request_queue.get()
            if request.request_type == "list_lights":
                self.response_queue.put(Response(self.hue.list_lights()))
            elif request.request_type == 'set_light_state':
                self.response_queue.put(Response(self.hue.set_light_state(request.light_id, request.payload)))
