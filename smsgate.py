#-*- coding:utf-8 -*-
import os
import requests
import sqlite3
import json
import logging

logging.basicConfig(filename='smsgate.log',format='%(asctime)s %(message)s', level=logging.INFO)

DEBUG= True
class SMSGate():
    def __init__(self, arg, service):
        self.arg = arg
        self.service = service
            
    def send(self, phone, msg):
        # api указанное на сайте и  api  в задании,они отличаются,
        # поэтому беру данные  из задания.
        d_output = {}
        url = self.arg.get('URL')
        post_data = dict()
        post_data[self.arg['MESSAGE']] = msg   # У разных сервисов могут быть разные ключи для полей
        post_data[self.arg['PHONE_NUMBER']] = phone #  сообщения и номера телефона. Поэтому их храним
                                                    #  в конфиге для каждого случая.
        post_data.update(self.arg['PARAMETRS'])     # добавляем параметры для сервиса в post запрос.
        ret_obj = requests.post(self.arg['URL'], data = post_data)  # post -запрос.
        ret = ret_obj.json()   # вытаскивает json объект из ответа.
        logging.info("%s :%s: %s:%s "%(self.service, phone, msg, ret))
        
        return ret
    
            
def get_handler(handler_name):
    service=dict()
    print 'load'
    with open('settings') as file:
        data = json.load(file)
    print data
    
    for  key, value in data.items():
        service[key] = SMSGate(value, key)
    
    ret = service.get(handler_name,None)
    return ret

if __name__ == '__main__':
    
      print "\
         #SMS GATE: Example.\n \
         import smsgate \n \
         \n \
         handler = smsgate.get_handler('smsc') \n \
         handler.send('+7926XXXXXXX','Hello world!')"
       

        
            
        
        
        
        



