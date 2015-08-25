# -*- coding: utf-8 -*-

from main import DOORPI

DOCUMENTATION = dict(
    fulfilled_with_one = False,
    text_description = '''
Der Event-Handler ist das Herz-Stück von DoorPi und die Vermittlerstelle zwischen den Events und Actions.
Bei Ihm müssen sich alle Module anmelden, die Events "abfeuern" können oder Actions bei bestimmten Events ausgelöst bekommen wollen.
Jedes Event für sich wird seriell (eins nach dem anderen) abgearbeitet. Mehrere Events werden parallel (alle auf einmal) ausgeführt.
Damit das parallele Ausführen von Actions möglich wird, arbeitet der Event-Handler mit Threads.

Die ausgelösten Events werden in einer Datenbank (SQLLite) gespeichert und können z.B. in der Weboberfläche ausgewertet werden.
''',
    events = [
        #dict( name = 'Vorlage', description = '', parameter = [ dict( name = 'param1', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ) ]),
    ],
    configuration = [
        #dict( json_path = 'resources/event_handler/event_log/typ', type = 'string', default = 'sqllite', mandatory = False, description = 'Typ der Event_Hanler Datenbank (aktuell nur sqllite)'),
    ],
    auto_install = dict(
        available = True,
        install = [],
        uninstall = [],
        update = []
    ),
    libraries = dict(
        threading = dict(
            mandatory =             True,
            text_warning =          '',
            text_description =      'Grundmodul für das Theardering, also die parallele Ausführung von Events.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          dict(
                standard = True
            ),
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import threading</code> eingeben wird.',
            text_configuration =    'Es ist keine Konfiguration vorgesehen.',
            configuration = [],
            text_links = {
                'docs.python.org': 'https://docs.python.org/%s/library/threading.html'%DOORPI.CONST.USED_PYTHON_VERSION
            }
        ),
        inspect = dict(
            mandatory =             True,
            text_warning =          '',
            text_description =      'Das Python-Modul inspect kann den Zustand eines laufenden Programms analysieren und Funktionen bzw. Objekte auswerten. Das wird z.B. bei der Parameterbestimmung der Actions benötigt um die Schnittstelle Event-Handler zu Action so abstrakt wie möglich halten zu können.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          dict(
                standard = True
            ),
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import inspect</code> eingeben wird.',
            text_configuration =    'Es ist keine Konfiguration vorgesehen.',
            configuration = [],
            text_links = {
                'docs.python.org': 'https://docs.python.org/%s/library/inspect.html'%DOORPI.CONST.USED_PYTHON_VERSION
            }
        ),
        sqlite3 = dict(
            mandatory =             True,
            text_warning =          '',
            text_description =      'SQLite is a C library that provides a lightweight disk-based database that doesn’t require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language. Some applications can use SQLite for internal data storage. It’s also possible to prototype an application using SQLite and then port the code to a larger database such as PostgreSQL or Oracle.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          dict(
                standard = True
            ),
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import sqlite3</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                dict( json_path = 'resources/event_handler/event_log/typ', type = 'string', default = 'sqllite', mandatory = False, description = 'Typ der Event_Handler Datenbank (aktuell nur sqllite)'),
                dict( json_path = 'resources/event_handler/event_log/connection_string', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/%s/library/sqlite3.html'%DOORPI.CONST.USED_PYTHON_VERSION
            }
        )
    )
)
