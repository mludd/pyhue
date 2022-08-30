# -*- coding: utf-8 -*-
import json
import pprint
import requests
from time import sleep
from threading import Thread


class Hue:
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.username = ''
        self.bridge = ''
        self.protocol = "http://"
        self.load_config()

    def load_config(self):
        """
        Loads configuration from self.CONFIG_FILE
        :return:
        """
        with open(self.CONFIG_FILE, 'r') as file:
            data = json.load(file)
            self.username = data['username']
            self.bridge = data['bridge']

    @staticmethod
    def print_msg(msg, quiet=False):
        """
        print() wrapper with quiet parameter
        :param msg:
        :param quiet:
        :return:
        """
        if not quiet:
            if isinstance(msg, list):
                for row in msg:
                    print(row)
            else:
                print(msg)

    def get_endpoint_url(self, endpoint):
        """
        Puts together a URL for specified endpoint
        :param endpoint:
        :return:
        """
        return self.protocol+self.bridge+"/api/"+self.username+"/"+endpoint

    def call_get(self, url):
        """
        Makes a GET request to specified URL and returns JSON data
        :param url:
        :return:
        """
        obj = json.loads(requests.get(url).text)
        return obj

    def call_put(self, url, body):
        """
        Makes a PUT request to specified URL and returns JSON data
        :param url:
        :param body:
        :return:
        """
        obj = json.loads(requests.put(url, body).text)
        return obj

    def parse_result(self, result):
        """
        Generates human-readable output based on general status message
        :param result:
        :return:
        """
        if "success" in result:
            return "Operation successful"
        elif "error" in result:
            return "Operation failed: "+result['error']['description']

    def list_lights(self):
        """
        Prints out a list of lights and whether they're on or off
        :return:
        """
        url = self.get_endpoint_url("lights")
        data = self.call_get(url)
        output = {}
        for light_id in data:
            light = data[str(light_id)]
            output[light_id] = light
        return output

    def get_light_state(self, light_id):
        """
        Fetches the current state of a light
        :param light_id:
        :return:
        """
        url = self.get_endpoint_url("lights")+"/"+str(light_id)
        data = self.call_get(url)
        return data

    def set_light_state(self, light_id, state):
        """
        Sets light state
        :param light_id:
        :param state:
        :return:
        """
        url = self.get_endpoint_url("lights")+"/"+str(light_id)+"/state"
        result = self.call_put(url, json.dumps(state))
        return result

    def turn_on_light(self, light_id):
        """
        Sets light state to On
        :param light_id:
        :return:
        """
        url = self.get_endpoint_url("lights/"+str(light_id)+"/state")
        body = '{"on": true}'
        result = self.call_put(url, body)
        return self.parse_result(result[0])

    def turn_off_light(self, light_id):
        """
        Sets light state to Off
        :param light_id:
        :return:
        """
        url = self.get_endpoint_url("lights/"+str(light_id)+"/state")
        body = '{"on": false}'
        result = self.call_put(url, body)
        return self.parse_result(result[0])

    def flash_light(self, light_id, flashes):
        """
        Turns light on and flashes it the specified number of times
        :param light_id:
        :param flashes:
        :return:
        """
        valid_attributes = ["on", "bri", "colormode", "hue", "sat", "xy", "ct"]
        original_state = {k: v for k, v in self.get_light_state(light_id).items() if k in valid_attributes}

        # This doesn't work, brightness still ends up being set to 0
        if original_state['on'] is not True:
            valid_attributes = ["on", "colormode", "hue", "sat", "xy", "ct"]
            original_state = {k: v for k, v in original_state.items() if k in valid_attributes}

        original_state['transitiontime'] = 0

        on_state = {
            "on": True,
            "bri": 254,
            "hue": 0,
            "transitiontime": 0
        }
        off_state = {
            "on": False,
            "transitiontime": 0
        }

        # Turn light on, max brightness
        self.turn_on_light(light_id)

        # turn off and on flashes - 1 times
        for i in range(flashes):
            self.set_light_state(light_id, off_state)
            sleep(0.2)
            self.set_light_state(light_id, on_state)
            sleep(0.2)

        # return to previous state
        self.set_light_state(light_id, original_state)
        return "Flashing done"
