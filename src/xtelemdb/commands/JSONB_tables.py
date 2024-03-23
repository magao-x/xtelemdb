'''
File contains all tables in JSONB supported format.;
might need to change to a single table for all telemetry, info...

Primary key geing both timestamp and jsonb creates 'and' on conflict.
'''


def create_telemetry():
    return '''
    CREATE TABLE IF NOT EXISTS telemetry(
    device VARCHAR(50),
    ts TIMESTAMP,
    prio VARCHAR(8),
    ec VARCHAR(20),
    msg JSONB,
    PRIMARY KEY (ts, msg)
    );
'''

def create_info():
    return '''
    CREATE TABLE IF NOT EXISTS info(
    device VARCHAR(50),
    ts TIMESTAMP,
    prio VARCHAR(8),
    ec VARCHAR(20),
    msg JSONB,
    PRIMARY KEY(ts, msg)
    );
'''

def create_fileSystem():
    return '''
    CREATE TABLE IF NOT EXISTS file_system(
    device VARCHAR(50),
    ts TIMESTAMP,
    ec VARCHAR(20),
    msg JSONB,
    PRIMARY KEY(ts, msg)
    );
'''

def create_backfill():
    return '''
    CREATE TABLE IF NOT EXISTS backLog(
    device VARCHAR(50),
    file VARCHAR(50),
    ts TIMESTAMP);

'''

def build_all():
    return create_telemetry(), create_info(), create_fileSystem(), create_backfill()
