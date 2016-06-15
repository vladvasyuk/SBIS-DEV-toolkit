import re
def _search_hooks(str_parse, list_hooks):
   for hook in list_hooks.items():
     try:
        if len(re.findall(hook[1], str_parse)) > 0:
           return True, hook[0]
     except KeyError:
        print('Not correct parametr "git_hooks_regxp" in confix.ini .')
   else:
      return False, ''

def search_in_diff(st, list_hooks):
   """
    проверяет diff на regex'ы из конфига 
   """
   b = st.split('\n')
   file_name = ''
   for item in b:
      if len(item) > 0 and item[0] == '+':
         if re.match('\+{3,}', item) is not None:
            if len(re.findall(r'[^/]*$', item)) > 0:
               file_name = re.findall(r'[^/]*$', item)[0]
         else:
            is_search, hook = _search_hooks(item, list_hooks)
            if is_search:
               return False, file_name + '   -   ' + hook
   else:
      return True, ''
