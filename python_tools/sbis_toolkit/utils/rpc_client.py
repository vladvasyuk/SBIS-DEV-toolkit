from http.client import HTTPConnection, HTTPSConnection, OK
from http.cookies import SimpleCookie
from datetime import datetime
import sys
import json
from time import time


class RpcClient:
   """
   Удаленный вызов методов БЛ

   >>> ADDRESS = "localhost:1001"
   >>> LOGIN = "Админ_тензор"
   >>> PSWD = "1234"
   >>> cl = RpcClient(ADDRESS, False)
   >>> cl.auth(LOGIN, PSWD)
   """

   def __init__(self, hostname, is_https=False):
      """Инициализация"""
      self.hostname = hostname
      self.header = {"Content-type": "application/json; charset=UTF-8"}
      self.timepass = {}
      self.connection = HTTPSConnection if is_https else HTTPConnection

   def auth(self, login=None, password=None, sid=None):
      """Авторизация"""
      if sid is None:
         sid = self.call("САП.Аутентифицировать", "/auth", 
               {
                  'login': login,
                  'password': password
               }
            )

      cookie = SimpleCookie()
      cookie["sid"] = sid
      self.header["Cookie"] = str(cookie)
      self.header["X-SBISSessionID"] = sid

      return sid

   def call(self, method, _site="", params={}):
      """Удаленный вызов метода БЛ"""
      body = json.dumps({"jsonrpc": "2.0", "method": method,
                         "params": params, "protocol": 3, "id": 1})

      # Запрашиваем
      conn = self.connection(self.hostname)
      started = datetime.now()  # Замер времени
      conn.request("POST", _site + "/service/sbis-rpc-service300.dll",
                   body, self.header)
      response = conn.getresponse()
      passed = (datetime.now() - started).total_seconds()

      # Читаем
      data = response.read()
      conn.close()

      # Проверяем
      if response.status is not OK:
         raise Exception("%d %s %s" % (response.status,
                                       response.reason, data.decode()))

      # Разбираем
      answer = json.loads(data.decode())
      if "error" in answer:
         raise Exception(answer["error"]["message"])
      if "result" not in answer:
         raise Exception("Ответ от сервера не содержит поле 'result'.")

      # Сохраняем замер времени
      if method not in self.timepass:
         self.timepass[method] = [passed]
      else:
         self.timepass[method].append(passed)

      # Возвращаем результат
      return answer["result"]
