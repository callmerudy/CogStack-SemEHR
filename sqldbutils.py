import utils as imutil
import pyodbc
import MySQLdb


#SQL db setting
dsn = 'sqlserverdatasource'
user = ''
password = ''
database = ''


def get_db_connection():
    con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    return {'cnxn': cnxn, 'cursor': cursor}


def get_db_connection_by_setting(setting_file):
    settings = imutil.load_json_data(setting_file)
    if 'db_type' in settings and settings['db_type'] == 'mysql_socket':
        return get_mysqldb_connection(settings['server'],
                                      settings['user'],
                                      settings['password'],
                                      settings['database'],
                                      settings['mysql_sock_file'])
    if 'trusted_connection' in settings:
        con_string = 'driver=%s;server=%s;trusted_connection=yes;DATABASE=%s;' % (settings['driver'],
                                                                         settings['server'],
                                                                         settings['database'])
    elif 'dsn' in settings:
        con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (settings['dsn'],
                                                            settings['user'],
                                                            settings['password'],
                                                            settings['database'])
    else:
        con_string = 'driver=%s;server=%s;UID=%s;PWD=%s;DATABASE=%s;' % (settings['driver'],
                                                                         settings['server'],
                                                                         settings['user'],
                                                                         settings['password'],
                                                                         settings['database'])
    # print pyodbc.drivers()
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    return {'cnxn': cnxn, 'cursor': cursor}


def get_mysqldb_connection(my_host, my_user, my_pwd, my_db, my_sock='/var/lib/mysql/mysql.sock'):
    db = MySQLdb.connect(host=my_host,  # your host, usually localhost
                         user=my_user,  # your username
                         passwd=my_pwd,  # your password
                         db=my_db,
                         unix_socket=my_sock)  # name of the data base
    cursor = db.cursor()
    return {'cnxn': db, 'cursor': cursor}


def release_db_connection(cnn_obj):
    cnn_obj['cnxn'].close()
    #cnn_obj['cursor'].close()
    #cnn_obj['cnxn'].disconnect()


def query_data(query, container, dbconn=None):
    if dbconn is None:
        conn_dic = get_db_connection()
    else:
        conn_dic = dbconn

    conn_dic['cursor'].execute(query)
    if container is not None:
        rows = conn_dic['cursor'].fetchall()
        columns = [column[0] for column in conn_dic['cursor'].description]
        for row in rows:
            container.append(dict(zip(columns, row)))
    else:
        conn_dic['cnxn'].commit()
    release_db_connection(conn_dic)
