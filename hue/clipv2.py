# -*- coding: utf-8 -*-
import json
import requests
import urllib3
from json import JSONDecodeError


class Clipv2:
    """
    Simple adapter class for communicating with the Philips Hue Clipv2 API
    """
    CONFIG_FILE = "config.json"
    VERIFY_SSL = False

    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.application_key = ''
        self.bridge = ''
        self.protocol = 'https://'
        self._load_config()

    def _load_config(self):
        """
        Loads configuration from self.CONFIG_FILE
        :return:
        """
        with open(self.CONFIG_FILE, 'r') as file:
            data = json.load(file)
            self.application_key = data['username']
            self.bridge = data['bridge']

    def _get_endpoint_url(self, endpoint):
        """
        Puts together a URL for specified endpoint
        :param endpoint:
        :return:
        """
        return self.protocol+self.bridge+'/clip/v2/'+endpoint

    def call_get(self, endpoint):
        """
        Makes a GET request to specified URL and returns JSON data
        :param endpoint:
        :return:
        """
        url = self._get_endpoint_url(endpoint)
        try:
            return json.loads(requests.get(url, verify=self.VERIFY_SSL,
                                           headers={"hue-application-key": self.application_key}).text)
        except JSONDecodeError:
            return False

    def call_put(self, endpoint, body):
        """
        Makes a PUT request to a specified URL and returns JSON data
        :param endpoint:
        :param body:
        :return:
        """
        url = self._get_endpoint_url(endpoint)
        try:
            return json.loads(requests.put(url, body, verify=self.VERIFY_SSL,
                                           headers={"hue-application-key": self.application_key}).text)
        except JSONDecodeError:
            return False

    def list_lights(self):
        """
        List all available lights
        :return:
        """
        data = self.call_get('resource/light')
        if data and type(data) != bool:
            output = {}
            for light in data['data']:
                output[light['id']] = light
            return output
        return False

    def turn_on_light(self, light_id):
        """
        Sets light state to on
        :param light_id:
        :return:
        """
        body = {
            'on': {
                'on': True
            }
        }
        return self.call_put('resource/light/'+light_id, json.dumps(body))

    def turn_off_light(self, light_id):
        """
        Sets light state to off
        :param light_id:
        :return:
        """
        body = {
            'on': {
                'on': False
            }
        }
        return self.call_put('resource/light/'+light_id, json.dumps(body))

    def set_light_state(self, light_id, state):
        """
        Sets the light state
        :param light_id:
        :param state:
        :return:
        """
        return self.call_put('resource/light/'+light_id, json.dumps(state))

    def get_light_state(self, light_id):
        """
        Gets current state of specified light
        :param light_id:
        :return:
        """
        data = self.call_get('resource/light/'+light_id)
        if data and type(data) != bool:
            return data['data'][0]

        return data
