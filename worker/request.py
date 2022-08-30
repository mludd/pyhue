# -*- coding: utf-8 -*-


class Request:
    def __init__(self, request_type, payload=None, light_id=None):
        self.request_type = request_type
        self.payload = payload
        self.light_id = light_id
