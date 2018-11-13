import connection
from datetime import datetime
from psycopg2 import sql


# def get_list_of_questions():
#     questions = connection.read_from_file('./sample_data/question.csv')
#     return questions


@connection.connection_handler
def get_list_of_questions_sql(cursor):
    cursor.execute('''SELECT * FROM question;
                    ''')
    questions = cursor.fetchall()
    return questions


# def get_list_of_answers():
#     answers = connection.read_from_file('./sample_data/answer.csv')
#     return answers


@connection.connection_handler
def get_list_of_answer_sql(cursor):
    cursor.execute('''SELECT * FROM answer;
                        ''')
    answer = cursor.fetchall()
    return answer


# def get_question_details(question_id):
#     questions = connection.read_from_file('./sample_data/question.csv')
#     question = {}
#     for row in questions:
#         if row['id'] == question_id:
#             question = row
#     return question


@connection.connection_handler
def get_question_details_sql(cursor, question_id):
    cursor.execute('''SELECT * FROM question
                        WHERE id = %(question_id)s;
                        ''',
                   {'question_id': question_id}
                   )
    actual_questions = cursor.fetchone()
    return actual_questions


# def get_answers_for_question(question_id):
#     answers = connection.read_from_file('./sample_data/answer.csv')
#     answers_for_question = []
#     for row in answers:
#         if row['question_id'] == question_id:
#             answers_for_question.append(row)
#     return answers_for_question


@connection.connection_handler
def get_answers_for_question_sql(cursor, question_id):
    cursor.execute('''SELECT * FROM answer
                            WHERE question_id = %(question_id)s;
                            ''',
                   {'question_id': question_id}
                   )
    answers_for_question = cursor.fetchall()
    return answers_for_question


# def convert_to_date(date_in_seconds):
#     time = datetime.fromtimestamp(date_in_seconds)
#     return time


# def write_question_to_csv(row):
#     fieldnames = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
#     connection.write_to_file('./sample_data/question.csv', row, fieldnames)


@connection.connection_handler
def insert_data_into_question(cursor, dicti):
    query = """insert into question values (%(id)s, %(submission_time)s, %(view_number)s, %(vote_number)s,
             %(title)s, %(message)s, %(image)s)"""
    params = dicti
    cursor.execute(query, params)


@connection.connection_handler
def insert_data_into_answer(cursor, dicti):
    query = """insert into answer values (%(id)s, %(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s,
            %(image)s)"""
    params = dicti
    cursor.execute(query, params)


# def write_answer_to_csv(row):
#     fieldnames = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
#     connection.write_to_file('./sample_data/answer.csv', row, fieldnames)
#
#
# def generate_id(table):
#     highest_id = 0
#     for row in table:
#         if int(row["id"]) > highest_id:
#             highest_id = int(row["id"])
#     return highest_id + 1


@connection.connection_handler
def generate_sql_id(cursor, table):
    query = sql.SQL("""SELECT MAX(id) FROM {}""").format(sql.Identifier(table))
    cursor.execute(query)
    max_id = cursor.fetchone()
    if max_id['max'] is None:
        max_id['max'] = 0
    return max_id['max'] + 1


# def overwrite_answer_in_file(table):
#     fieldnames = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
#     connection.overwrite_file('./sample_data/answer.csv', fieldnames, table)


@connection.connection_handler
def edit_question(cursor, question_id, dicti):
    query = """UPDATE question SET submission_time = %(submission_time)s, title = %(title)s, message = %(message)s, image = %(image)s
            WHERE id = %(question_id)s"""
    params = dicti
    cursor.execute(query, params)


# def overwrite_question_in_file(table):
#     fieldnames = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
#     connection.overwrite_file('./sample_data/question.csv', fieldnames, table)
#

# @connection.connection_handler
# def delete(cursor, table, id):
#     query = sql.SQL("""DELETE FROM {} WHERE id = %(id)s""").format(
#     sql.Identifier(table))
#     cursor.execute(query, {'id': id})


@connection.connection_handler
def delete_question(cursor, id):
    cursor.execute('''DELETE FROM question_tag WHERE question_id=%(question_id)s;
                    ''', {'question_id': id})
    cursor.execute('''SELECT id FROM answer WHERE question_id=%(question_id)s;
                        ''', {'question_id': id})
    answer_ids = cursor.fetchall()
    for answer_id in answer_ids:
        cursor.execute('''DELETE FROM comment WHERE answer_id=%(answer_id)s;
                        ''', {'answer_id': answer_id['id']})
    cursor.execute('''DELETE FROM comment WHERE question_id=%(id)s;
                          ''', {'id': id})
    cursor.execute('''DELETE FROM answer WHERE question_id=%(id)s;
                          ''', {'id': id})
    cursor.execute('''DELETE FROM question WHERE id=%(id)s;
                    ''', {'id': id})


@connection.connection_handler
def delete_answer(cursor, id):
    cursor.execute('''DELETE FROM answer WHERE id=%(answer_id)s;
                      ''', {'answer_id': id})


@connection.connection_handler
def delete_comment(cursor, id):
    cursor.execute('''DELETE FROM comment WHERE id=%(question_id)s;
                      ''', {'id': id})


@connection.connection_handler
def delete_question_comment(cursor, id, question_id):
    cursor.execute('''DELETE FROM comment WHERE id=%(id)s AND question_id=%(question_id)s;
                      ''', {'id': id, 'question_id': question_id})


@connection.connection_handler
def delete_answer_comment(cursor, id, answer_id):
    cursor.execute('''DELETE FROM comment WHERE id=%(id)s AND answer_id=%(answer_id)s;
                      ''', {'id': id, 'answer_id': answer_id})


# def updates_vote(filter_id, rows, vote_modifier):
#     for row in rows:
#         if row['id'] == filter_id:
#             row['vote_number'] = int(row['vote_number']) + vote_modifier


@connection.connection_handler
def update_vote_sql(cursor, vote_modifier, table, id):
    query = sql.SQL("""UPDATE {} SET vote_number = vote_number + %(vote_modifier)s WHERE id = %(id)s""").format(
        sql.Identifier(table))
    cursor.execute(query, {'vote_modifier': vote_modifier, 'id': id})


def sort_by(table, sorting_by, order):
    if sorting_by in ["message", "title"]:
        lambda_expression = lambda k: k[sorting_by].lower()
    elif sorting_by in ["vote_number"]:
        lambda_expression = lambda k: int(k[sorting_by])
    else:
        lambda_expression = lambda k: k[sorting_by]
    try:
        if order == "ascending":
            sorted_table = sorted(table, key=lambda_expression)
        else:
            sorted_table = sorted(table, key=lambda_expression, reverse=True)
        return sorted_table
    except KeyError:
        print("KEY NOT FOUND, RETURNING THE UNSORTED TABLE")
        return table


@connection.connection_handler
def update_view_sql(cursor, question_id):
    query = """UPDATE question SET view_number = view_number + 1 WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})


@connection.connection_handler
def sort_sql(cursor, table, column, ascending):
    if ascending is True:
        query = sql.SQL("SELECT * FROM  {0} ORDER BY {1} ASC ").format(
            sql.Identifier(table), sql.Identifier(column))
    else:
        query = sql.SQL("""SELECT * FROM  {0} ORDER BY {1} DESC """).format(
            sql.Identifier(table), sql.Identifier(column))
    cursor.execute(query)
    table = cursor.fetchall()
    return table


@connection.connection_handler
def sort_answer_sql(cursor, question_id):
    query = "SELECT * FROM  answer WHERE question_id = %(question_id)s ORDER BY vote_number DESC"
    cursor.execute(query, {'question_id': question_id})
    table = cursor.fetchall()
    return table


@connection.connection_handler
def get_comments_sql(cursor):
    query = """SELECT * FROM comment """
    cursor.execute(query)
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def update_question_comment(cursor, dicti):
    query = """INSERT INTO comment (id, question_id, message, submission_time, edited_count) 
                VALUES (%(id)s, %(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s)"""
    params = dicti
    cursor.execute(query, params)


@connection.connection_handler
def update_answer_comment(cursor, dicti):
    query = """INSERT INTO comment (id, answer_id, message, submission_time, edited_count)
                VALUES (%(id)s, %(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s)"""
    params = dicti
    cursor.execute(query, params)


@connection.connection_handler
def search_by_keyword_question(cursor, keyword):
    cursor.execute('''
                    SELECT * FROM question
                    WHERE question.title LIKE %(keyword)s OR question.message LIKE %(keyword)s;
                    ''',
                   {'keyword': '%' + keyword + '%'})
    result = cursor.fetchall()
    return result


@connection.connection_handler
def search_by_keyword_answer(cursor, keyword):
    cursor.execute('''
                    SELECT * FROM answer
                    WHERE answer.message LIKE %(keyword)s;
                    ''',
                   {'keyword': '%' + keyword + '%'})
    result = cursor.fetchall()
    return result
