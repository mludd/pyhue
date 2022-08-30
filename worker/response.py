# -*- coding: utf-8 -*-


class Response:
    def __init__(self, payload, light_id=None):
        self.payload = payload
        self.light_id = light_id
