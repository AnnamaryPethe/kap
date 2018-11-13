import csv, os, psycopg2, psycopg2.extras

def read_from_file(filename):
    with open(filename) as file:
        table = []
        reader = csv.DictReader(file)
        for row in reader:
            table.append(row)

    return table

def write_to_file(filename,row,fieldnames):
    with open(filename, "a") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(row)


def overwrite_file(filename,fieldnames,table):
    with open(filename, "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in table:
            writer.writerow(item)


def get_connection_string():
    # setup connection string
    # to do this, please define these environment variables first
    user_name = os.environ.get('PSQL_USER_NAME')
    password = os.environ.get('PSQL_PASSWORD')
    host = os.environ.get('PSQL_HOST')
    database_name = os.environ.get('PSQL_DB_NAME')

    return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
        user_name=user_name,
        password=password,
        host=host,
        database_name=database_name
    )


def open_database():
    try:
        connection_string = get_connection_string()
        connection = psycopg2.connect(connection_string)
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print('Database connection problem')
        raise exception
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value

    return wrapper
