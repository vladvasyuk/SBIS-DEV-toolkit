from sbis_toolkit.utils.converting import convert_rs
import re

def get_doc_info_by_number(number, rpc_cli):
   """
   Получить описание документа по его номеру

   :param number:
   :param rpc_cli:
   """
   doc = get_doc_by_number(number, rpc_cli)

   if not doc:
      raise Exception('Документ не найден!')

   return ('https://inside.tensor.ru/opendoc.html?guid={guid}\n'
           '{type_title} от {doc_date} №{doc_number}\n'
           '{doc_text}\n'
          ).format(
      type_title=doc['ТипДокумента.НазваниеКраткое'],
      doc_date=doc['Документ.Дата'],
      doc_number=doc['Документ.Номер'],
      doc_text=re.sub('<[^<]+?>', '', doc['РазличныеДокументы.Информация'])[:100] + '...',
      guid=doc['ИдентификаторДокумента']
   )

def get_doc_by_number(number, rpc_cli):
   """
   Получить документ по его номеру

   :param number:
   :param rpc_cli:
   """
   filter_params = {
      "Фильтр": {
         "s": [],
         "d": [],
         "_type": "record"
      },
      "Сортировка": None,
      "Навигация": {
        "s": [
            {
               "n": "ЕстьЕще",
               "t": "Логическое"
            },
            {
               "n": "РазмерСтраницы",
               "t": "Число целое"
            },
            {
               "n": "Страница",
               "t": "Число целое"
            }
         ],
            "d": [
               True,
               1000,
               0
            ],
            "_type": "record"
       },
       "ДопПоля": []
   }
   res = rpc_cli.call("СвязьПапок.ДокументыВПапке", params=filter_params)

   rs = convert_rs(res)

   for doc in rs:
      if doc['Документ.Номер'] == str(number):
         return doc
