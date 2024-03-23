'''
This file is used for direct admin access to xtelem database for adding, droping, and creating data to and from db. 
'''

import psycopg2
from psycopg2 import sql
import json
import os
from . import JSONB_tables as jt
import logging
import logging.handlers
import threading
import glob
'''
logger information here
'''

db_params = {
        "host": "localhost",
        "dbname": "xtelem",
        "user": "tsnedden", #input() too?
        "port": "5432",
    }

tables = ['telemetry', 'info', 'file_system', 'backfill']

class FileIngester():
    '''ingest archived data files into the database. Data will be processed and seperated into backlog table consisting of device, file, and timestamp. Files will then be further processed and inserted into the corrosponding tables.'''
    def __inti__(self):
        self.db_params = db_params
        self.dirs = ['/opt/MagAOX/telem', '/opt/MagAOX/logs', '/opt/MagAOX/rawimages/*/']
    #create thread targets
    def file_ingest(self, dir):
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                try:
                    if os.path.isdir(dir):
                        print(f'Processing directory {dir}.')
                        for file in glob.glob(os.path.join(dir, '*.json')): # '/*.json' is a wildcard for all json files
                            with open(file, 'r') as jFile:
                                for line in jFile:
                                    data_input(line, cur, conn)

                                    #insert backfill db
                                        # insert device, file, timestamp
                except Exception as e:
                    print(e)
                    conn.rollback()
                    print('Data not added. Rolled back')
    
    def file_threads(self):
        '''create threads for each file in directory'''
        threads= []
        for dir in self.dirs:
            t = threading.Thread(target = self.file_ingest, args = dir, daemon= True) #daemon = True will kill the thread if main thread is killed
            t.start()
            threads.append(t)
        
        #wait for threads
        for thread in threads:
            thread.join()

    
def create_user(name= 'guest' , pw= None, role= "SELECT"):
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute(f'''CREATE USER {name} WITH PASSWORD {pw};''')
            cur.execute(f'''GRANT CONNECT ON DATABASE xtelem TO {name};''')
            cur.execute(f'''GRANT SELECT ON ALL TABLES IN SCHEMA public TO {name};''')
            cur.commit()
    return None

def backup():
    '''back up the tables.'''
    pass

def truncateAll():
    '''truncate delets information in table, not table itself. faster than deleting too'''
    pass
def drop_table(tableName):
    '''delete a single table'''
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE {tableName}")

def dropAll():
    ''''deletes all table in db xtelem'''
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            # add a are you sure option
            for x in tables:
                cur.execute(f"DROP TABLE IF EXISTS {x} CASCADE;")
                print(f"Dropped table {x}")

def create_tables():
    '''create all table s in JSONB_table.py if not already exitsts'''
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                imported_tables = jt.build_all()
                for ind, table in enumerate(imported_tables):
                    cur.execute(table)
                    print(f'{tables[ind]} created')
                conn.commit
    except Exception as e:
        print(e)
        conn.rollback()
        print('Tables not created.\nExecuted rollback')

def data_input(json_line, cur, conn):
    '''
    add JSON lines to database tables. db is opened from watcher
    '''
    try:
                json_data = json.loads(json_line)
                if json_data['device'].strip().lower() == 'filesystem':
                    cur.execute('''
                                INSERT INTO file_system (device, ts, ec, msg)
                                VALUES (%s, %s, %s, %s::JSONB)
                                ON CONFLICT (ts, msg) DO NOTHING;
                                ''' , (json_data['device'], json_data['ts'], \
                                       json_data['ec'], json.dumps(json_data['msg'])))
                    print(f'Added {json_data} to File_System')

                elif json_data['prio'] == 'TELM':   
                    cur.execute('''
                                INSERT INTO telemetry (device, ts, prio, ec, msg) 
                                VALUES (%s, %s, %s, %s, %s::JSONB) 
                                ON CONFLICT (ts, msg) DO NOTHING;
                                ''', (json_data['device'], json_data['ts'], \
                                      json_data['prio'], json_data['ec'], json.dumps(json_data['msg'])))
                    print(f'Added {json_data} to telem')

                elif json_data['prio'].strip().lower() in ['info', 'err', 'note', 'warn']: # THERE is a space in 'ERR ' in json line
                    cur.execute('''
                                INSERT INTO info (device, ts, prio, ec, msg)
                                VALUES (%s, %s, %s, %s, %s::JSONB)
                                ON CONFLICT (ts, msg) DO NOTHING;
                                ''', (json_data['device'], json_data['ts'], \
                                      json_data['prio'], json_data['ec'], json.dumps(json_data['msg'])))
                    print(f'Added {json_data} to info')
                          
    except Exception as e:
        print(e)
        with open('not_added.json', 'a') as output:
            output.write(str(json_data)+'\n')
        conn.rollback()


if __name__ == "__main__":
    while True:
        print('''
            1. Drop all table
            2. Create tables
            3. Drop single table
            4. Ingest archive data
            9. Exit
            ''')
        usr_inp = int(input("select an option from above:  "))

        if usr_inp == 1:
            dropAll()
        elif usr_inp == 2:
            create_tables()
        elif usr_inp == 3:
            drop_table()
        elif usr_inp == 4:
            ingest = FileIngester()
            ingest.file_threads()
        elif usr_inp == 9:
            print('GoodBye')
            exit()
        else:
            print('not a valid input.')



