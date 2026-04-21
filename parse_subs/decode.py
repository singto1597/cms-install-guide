#!/usr/bin/env python3

import pickle
import sys
import json
import os
from urllib.parse import urlparse
import psycopg2

def load_dotenv(path='.env'):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        os.environ[key] = value.strip('"').strip("'")
                    except ValueError:
                        pass

load_dotenv()
CMS_CONF_FULL_PATH = os.environ.get('CMS_CONF_FULL_PATH', '/usr/local/etc/cms.conf')

ext_map = {
    'C# / Mono': 'cs',
    'C++ / g++': 'cpp',
    'C++14 / g++': 'cpp',
    'C++17 / g++': 'cpp',
    'C++20 / g++': 'cpp',
    'C11 / gcc': 'c',
    'Go': 'go',
    'Haskell / ghc': 'hs',
    'Java / JDK': 'java',
    'JavaScript / NodeJS': 'js',
    'JavaScript / bun': 'js',
    'Prolog / swipl': 'pl',
    'Python 3 / CPython': 'py',
    'Python 3.8 / CPython': 'py',
    'Python 3.10 / CPython': 'py',
    'Python 3.10 / PyPy': 'py',
    'Racket': 'rkt',
    'Ruby': 'rb',
    'Rust': 'rs',
    'SML / mosml': 'sml',
    'Shell script / bash': 'sh',
    'JavaScript / bun': 'ts'
}

def get_db_info(ts, default):
    with open(CMS_CONF_FULL_PATH, 'r') as f:
        cms_conf = json.load(f)

    database_url = cms_conf["database"]
    parsed_url = urlparse(database_url)
    
    conn = psycopg2.connect(
        dbname=parsed_url.path[1:],
        user=parsed_url.username,
        password=parsed_url.password,
        host=parsed_url.hostname,
        port=parsed_url.port
    )
    cursor = conn.cursor()

    query = """
        SELECT tasks.name, submissions.language
        FROM submissions
        JOIN tasks ON submissions.task_id = tasks.id
        WHERE submissions.timestamp = %s
    """
    cursor.execute(query, (ts,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if result:
        task_name = result[0]
        lang_name = result[1]
        type_ = ext_map.get(lang_name, default)
        return task_name, type_

    return "UnknownTask", default


def main():
    user_id = sys.argv[2]
    default_ext = sys.argv[4]
    time_string = sys.argv[3]

    with open(sys.argv[1], 'rb') as f:
        try:
            data = pickle.load(f)
        except pickle.UnpicklingError:
            print(sys.argv[1], "ERROR")
            sys.exit(1)

        raw = (data)[3]
        text = raw.popitem()
        
        task_id = text[0].split('.')[0].replace(' ', '_')
        content = text[1]

        content_decoded = None
        try:
            content_decoded_U = content.decode("utf-8")
        except:
            content_decoded = content.decode("tis-620")

        if not content_decoded:
            try:
                content_decoded_T = content.decode("tis-620")
            except:
                content_decoded = content.decode("utf-8")

        if not content_decoded:
            if len(content_decoded_U) <= len(content_decoded_T):
                content_decoded = content_decoded_U
            else:
                content_decoded = content_decoded_T

        ts = sys.argv[1].rsplit('/', maxsplit=1)[-1]
        
        db_task_name, type_ = get_db_info(ts, default_ext)

        
        if not task_id:
            task_id = db_task_name

        print(task_id, type_)
        
        if not content_decoded.endswith('\n'):
            content_decoded = content_decoded+'\n'
            
        filename = task_id + "_" + user_id + "_" + time_string + ".RAW"
        with open(filename, 'w+', encoding='utf-8') as out:
            out.write(content_decoded)

if __name__ == "__main__":
    main()
