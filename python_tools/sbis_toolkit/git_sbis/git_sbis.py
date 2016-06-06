import sbis_toolkit
from sbis_toolkit.utils.rpc_client import RpcClient
from sbis_toolkit.bl_methods import docs
from git import Repo
from urllib.parse import quote
import configparser
import base64
import os
import re
import git
import argparse
import sys
import webbrowser


MR_URL = "https://git.sbis.ru/{repo}/merge_requests/new?merge_request%5Bsource_branch%5D={source}&merge_request%5Btarget_branch%5D={target}"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(sbis_toolkit.__file__))) + '\\config.ini'


class DefaultHelpParser(argparse.ArgumentParser):
   def error(self, message):
      sys.stderr.write('error: %s\n' % message)
      self.print_help()
      sys.exit(2)


def parse_branch_name(name):
   """
   Разобрать название ветки на составляющие

   :param name: название ветки

   Ex.: 3.7.3.200/bugfix/capital/capitalname-style-fix-1172833927
   """
   values = re.findall(r"^(.+?)\/(.+?)(\d+)$", name)

   if not values or len(values[0]) != 3:
      print('Wrong current branch name.')
      sys.exit(1)

   return {
      'parent_branch': values[0][0],
      'task_number': values[0][2]
   }


def get_current_repo():
   """
   Получить текущий репозиторий
   """
   return Repo(os.getcwd())


def get_current_branch_name():
   """
   Получить название текущей ветки
   """
   return get_current_repo().active_branch.name


def commit_by_task(branch_name):
   """
   Сделать коммит с сообщением содержащим информацию о задаче

   :param branch_name:
   """
   info = docs.get_doc_info_by_number(
      parse_branch_name(branch_name)['task_number'], get_rpc_cli())
   get_current_repo().index.commit(message=info)
   return True


def get_branches_for_mr():
   """
   Получить ветки, в которые нужно создать merge request
   """
   res = ['development']
   cur_branch_name = parse_branch_name(get_current_branch_name())['parent_branch']

   if cur_branch_name != 'dev':
      rc_branches = get_rc_branches()
      cur_branch_val = get_branch_value(cur_branch_name)

      for rc_branch in rc_branches:
         if cur_branch_val <= get_branch_value(rc_branch.name):
            res.append(rc_branch.name)

   return res


def get_branch_value(branch_name):
   """
   Получить цифровое представление ветки

   :param branch_name:
   """
   return int(''.join(re.findall(u'\d', branch_name)))


def get_rc_branches():
   """
   Получить rc-ветки
   """
   repo = get_current_repo()
   return filter(lambda b: True if b.name.find('rc-') == 0 else False, repo.branches)


def get_current_repo_name():
   """
   Получить название текущего репозитория
   """
   repo = get_current_repo()
   return re.match(u'git@git.sbis.ru:(.+)\.git', repo.remote().url).groups()[0]


def open_mr_page(source, target):
   """
   Открывает в браузере вкладки с MR

   :param source:
   :param target:
   """
   webbrowser.open_new_tab(MR_URL.format(
         repo=get_current_repo_name(),
         source=source,
         target=target
      )
   )


def command_ci(args):
   """
   Команда - коммит с сообщением
   """   
   commit_by_task(get_current_branch_name())


def command_acp(args):
   """
   Команда - add, commit, push
   """
   repo = get_current_repo()
   cur_branch = get_current_branch_name()
   repo.git.add(u=True)

   if commit_by_task(cur_branch):
      repo.remotes.origin.push(cur_branch)

      for br in get_branches_for_mr():
         open_mr_page(cur_branch, br)


def command_cp(args):
   """
   Команда - commit, push
   """
   repo = get_current_repo()
   cur_branch = get_current_branch_name()
   if commit_by_task(cur_branch):
      repo.remotes.origin.push(cur_branch)

      for br in get_branches_for_mr():
         open_mr_page(cur_branch, br)


def get_rpc_cli():
   """
   Получить экземпляр RPC-клиента
   При первом вызове инициазилирует клиент (авторизуется на сервере inside)
   """
   try:
      instance = get_rpc_cli.__instance__
   except AttributeError:
      config = configparser.ConfigParser()
      config.read(CONFIG_PATH)

      rpc_cli = RpcClient('inside.tensor.ru', False)

      try:
         login = config['sbis.user']['login']
         password = config['sbis.user']['password']
         if not (login and password):
            raise KeyError
      except KeyError:
         print('No sbis login credentials. Use "config" command.')
         sys.exit(1)

      rpc_cli.auth(login, password)

      get_rpc_cli.__instance__ = rpc_cli

   return get_rpc_cli.__instance__


def command_config(args):
   """
   Команда - конфигурация
   """
   config = configparser.ConfigParser()
   config.read(CONFIG_PATH)

   if args.section and args.argument and args.value:
      config[args.section][args.argument] = args.value
   else:
      print('Wrong config format.')
      sys.exit(1)

   with open(CONFIG_PATH, 'w') as configfile:
      config.write(configfile)


def command_mr(args):
   """
   Команда - открыть MRs в браузере
   """
   for br in get_branches_for_mr():
      open_mr_page(get_current_branch_name(), br)


if __name__ == '__main__':
   parser = DefaultHelpParser(prog='Git toolchain for SBIS developers.')
   subparsers = parser.add_subparsers(dest='cmd')
   subparsers.required = True

   ci_parser = subparsers.add_parser('ci', help='Commit with task info as a message.')
   ci_parser.set_defaults(func=command_ci)

   mr_parser = subparsers.add_parser('mr', help='Open merge requests in git.sbis.ru.')
   mr_parser.set_defaults(func=command_mr)

   cp_parser = subparsers.add_parser('cp', help='gs ci && git push origin HEAD && gs mr')
   cp_parser.set_defaults(func=command_cp)

   acp_parser = subparsers.add_parser('acp', help='git add -u && gs ci && git push origin HEAD && gs mr')
   acp_parser.set_defaults(func=command_acp)

   conf_parser = subparsers.add_parser('config', help='Change config.')
   conf_parser.add_argument('section')
   conf_parser.add_argument('argument')
   conf_parser.add_argument('value')
   conf_parser.set_defaults(func=command_config)

   args = parser.parse_args()
   args.func(args)
