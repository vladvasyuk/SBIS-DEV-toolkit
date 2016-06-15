#SBIS DEV toolkit

Набор утилит для разработчиков SBIS

##SBISPythonToolkit
------------

**git sbis**  
Обертки для команд git для оптимизации процесса работы с репозиториями sbis
по TensorFlow.

###Установка

Перейти в директорию python_tools, а затем выполнить:
```
python setup.py install
```

**git sbis**  
Для доступа к утилите по алиасу "gs", необходимо поместить
gs или gs.bat (в зависимости от ОС) в директорию, которую видит командная строка.
Либо (для linux/mingw/cygwin) добавить в .bashrc:
```
alias gs="python -m sbis_toolkit.git_sbis.git_sbis"
```

###Начало работы

**git sbis**  
Вначале необходимо указать учетные данные для авторизации на inside.sbis.ru:

```
gs config sbis.user login %ваш_логин%  
gs config sbis.user password %ваш_пароль%  
```

Затем перейти в директорию с репозиторием.
Для корректной работы с утилитой ветки должны именоваться с добавлением в конце номера задачи.
Например:

```
3.7.3.200/bugfix/some-branch-name-127811827
```

По номеру задачи будет получен текст для коммита.

Доступны следующие команды:

 - gs **ci** - создает коммит с текстом задачи
 - gs **mr** - открывает merge-request'ы на gitlab в соответствующие ветки
 - gs **cp** - соответствует ```gs ci && git push origin HEAD && gs mr```
 - gs **acp** - соответствует ```git add -u && gs ci && git push origin HEAD && gs mr```
 - gs **vacp** - проверяет валидацию и далее ```git add -u && gs ci && git push origin HEAD && gs mr```
 - gs **vcp** - проверяет валидацию и далее ```gs ci && git push origin HEAD && gs mr```
 - gs **config** - настройки утилиты
