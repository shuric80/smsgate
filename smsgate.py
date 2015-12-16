#-*- coding:utf-8 -*-
import sys
import os
from urllib import urlopen
import json
import sqlite3
from datetime import datetime
import re

LOGIN = 'user'
PASSWORD = 'password'
DEBUG= True
"""
В settings хранится json файл вида.
{
 "имя_сервиса":{
                "http":"https", #протокол
                "url":"//sms.ru", #url-адрес
                "script":"send.php" #
                "message":"txt" #
                "password":"psw",
                "login":"login",
                 "parametrs":{ #тут различные параметры для настройки
                              "a":"a",
                               .....
                               "z":"z"
                              }
               }
...
}
  """
class SMSGate():
    def __init__(self, json_arg, name):
        # l - словарь со всеми настройками для сервиса.
        self.l = json_arg
        self.name_service = name
        
        db_exist = os.path.isfile('smsgate.db')
        self._conn = sqlite3.connect('smsgate.db')
        self._cur = self._conn.cursor()

        if not db_exist:
          self._cur.execute('''CREATE TABLE log_sms (date text, phone text, message text, ret text)''')
          self._conn.commit()
    
    def send(self, phone, msg):
        # param - читаются из json файла параметры и формируется строка.
        param = '&'.join([ '='.join((key, value)) for key, value in self.l['parametrs'].items()])
        # формируется url 
        url = self.l['http'] + self.l['url'] +'/'+ self.l['script']
        # аргументы для POST
        ls_arg =  [
            [self.l['password'],PASSWORD],
            [self.l['login'],LOGIN],
            [self.l['message'],msg],
            [self.l['phone'],str(phone)]
            
        ]
        arg = '&'.join(['='.join(i) for i in ls_arg ])
        arg = arg+'&'+param
        # для отладки записываю в файл и эмулируем ответ.
        if DEBUG:
            f =open('debug','a')
            f.write('URL:%s\tPOST:%s'%(url,arg))
            f.write('\n')
            f.close()
            xml_ret = "<sms><status>status</status><last_date>last_date</last_date><last_timestamp>last_timestamp</last_timestamp><err>err</err></sms>"
        else:
            xml_ret = urlopen(url, arg.encode(CHARSET)).data()
        #парсим
        ret_dict = re.findall('(\w+)>(\w+)</',xml_ret)
        # превращаем в json формат
        ret = json.dumps(dict(ret_dict))
        # логгируем в БД
        self.log(phone,msg,ret)
        return ret
    
    def log(self,phone, msg, ret):
        log_data =(datetime.now(), phone, msg, ret)
        self._cur.execute("INSERT INTO log_sms VALUES(?,?,?,?)",log_data)
        self._conn.commit()
        
def get_handler(handler_name):
    service=dict()
    #читаем json файл
    with open('settings') as file:
        data = json.load(file)
    # создаем объекты , заносим в них данные.Сами объекты собираем в словарь.
    for  key, value in data.items():
        service[key] = SMSGate(value, key)
    #возвращаем объект по индексу. Если его нету, идет None    
    ret = service.get(handler_name,None)
    return ret

            
        
            
        
        
        
        



