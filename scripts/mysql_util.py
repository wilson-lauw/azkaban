import time
import sys
import traceback

import MySQLdb
max_retries = 3
retries_interval = 10

def get_db_cur(host,user,passwd,db,dictCursor=False):
    db = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=db,
        charset='utf8'
    )
    if dictCursor:
        cur = db.cursor(MySQLdb.cursors.DictCursor)
    else:
        cur = db.cursor()
    cur.connection.autocommit(True)

    return db, cur

def mysql_fetch(sql,host,user,passwd,db,dictCursor=True):
    retry_counter = 0
    while retry_counter < max_retries:
        try:
            db, cur = get_db_cur(host,user,passwd,db,dictCursor)
            print('executing mysql statement ' + sql)
            start = time.time()
            cur.execute(sql)
            end = time.time()
            data = cur.fetchall()
            print('Elapsed: ' + str((end-start) * 1000) + ' ms')
            cur.close()
            db.close()
            return data
        except Exception as ex:
            retry_counter += 1
            print('MySQL Fetch exception')
            print('Try number ' + str(retry_counter))
            print(traceback.format_exc())
            time.sleep(retries_interval)

    raise Exception('MySQL fetch failed')

def mysql_execute(sql,host,user,passwd,db):
    success = False
    retry_counter = 0
    while retry_counter < max_retries and not success:
        retry_counter += 1
        try:
            db, cur = get_db_cur(host,user,passwd,db)
            if type(sql) == type([]):
                for sta in sql:
                    print('executing mysql statement ' + sta)
                    start = time.time()
                    cur.execute(sta)
                    end = time.time()
                    print('Elapsed: ' + str((end-start) * 1000) + ' ms')
            else:
                print('executing mysql statement ' + sql)
                start = time.time()
                cur.execute(sql)
                end = time.time()
                print('Elapsed: ' + str((end-start) * 1000) + ' ms')
            cur.close()
            db.close()
            success = True
        except Exception as ex:
            print('MySQL Execute exception')
            print('Try number ' + str(retry_counter))
            print(traceback.format_exc())
            time.sleep(retries_interval)

    if not success:
        raise Exception('MySQL fetch failed')