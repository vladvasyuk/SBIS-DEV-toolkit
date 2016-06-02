def convert(data):
   """
   TODO
   """
   if (data['_type'] == 'recordset'):
      return convert_rs(data)
   elif (data['_type'] == 'record'):
      return convert_rec(data)

def convert_rec(data):
   """
   TODO
   """
   rec = {}
   for idx, val in enumerate(data['s']):
      rec[val['n']] = data['d'][idx]
   return rec

def convert_rs(data):
   """
   TODO
   """
   rs = []
   col_idx = []
   for idx, val in enumerate(data['s']):
      col_idx.append(val['n'])
   for rec in data['d']:
      res_rec = {}
      for idx, val in enumerate(rec):
         res_rec[col_idx[idx]] = val
      rs.append(res_rec)
   return rs
   