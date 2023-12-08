#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import urequests, gc
import ujson
from time import sleep
import json

gc.enable()

class Api():
    def __init__(self, controller, url, path, token, debug=False):
        self.URL = url
        self.TOKEN = token
        self.URL_PATH = path
        self.CONTROLLER = controller
        self.DEBUG = debug

    def upload(self, datas):
        if self.DEBUG:
            print('Api Uploading...')
            print('Datas: ', datas)

        if self.CONTROLLER.wifiIsConnected() == False:
            return False

        url = self.URL
        url_path = self.URL_PATH
        full_url = url + '/' + url_path
        token = self.TOKEN

        headers = {
            #'Content-type': 'form-data; charset=utf-8',
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + str(token),
        }

        try:
            response = urequests.post(
                full_url,
                headers=headers,
                data=(json.dumps(datas)).encode(),
                #data=datas,
                #json=ujson.dumps(datas),
                timeout=10
            )

        except Exception as e:
            if self.DEBUG:
                print('Error: ', e)

            return False
        finally:

            if self.DEBUG:
                print('Memoria antes de liberar: ', gc.mem_free())

            gc.collect()

            if self.DEBUG:
                print("Memoria después de liberar:", gc.mem_free())

        if self.DEBUG:
            print('payload: ', response.json())
            print('status code:', response.status_code)
            print('wifi status: ', self.CONTROLLER.wifiIsConnected())
