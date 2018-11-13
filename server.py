from flask import Flask, render_template, request, redirect, url_for
import data_manager
import datetime

app = Flask(__name__)


@app.route('/')
def index():
    ascending = True
    questions = data_manager.get_list_of_questions_sql()
    return render_template('index.html', questions=questions,ascending=ascending)


@app.route('/question/<question_id>/new-answer')
@app.route('/add-question')
def add_question(question_id=None):
    return render_template('post_form.html', question_id=question_id)


@app.route('/add-question', methods=['POST'])
def recieves_new_question():
    form_data = {'title': request.form['title'], 'message': request.form['message'],
                 'submission_time': datetime.datetime.now().replace(microsecond=0), 'vote_number': 0,
                 'id': data_manager.generate_sql_id('question'), 'view_number': 0, 'image': ''}
    data_manager.insert_data_into_question(form_data)
    return redirect('/')


@app.route('/question/<int:question_id>/new-answer', methods=['POST'])
def recieves_new_answer(question_id):
    answer_form = {'message': request.form['message'], 'question_id': question_id,
                   'id': data_manager.generate_sql_id('answer'),
                   'submission_time': datetime.datetime.now().replace(microsecond=0), 'vote_number': 0, 'image': ''}
    print(answer_form)
    data_manager.insert_data_into_answer(answer_form)
    return redirect('/question/{}'.format(question_id))


@app.route('/question/<int:question_id>')
def question_details(question_id):
    url = request.url
    comment = data_manager.get_comments_sql()
    actual_question = data_manager.get_question_details_sql(question_id)
    answers_for_question = data_manager.sort_answer_sql(question_id)
    return render_template('question_detail.html', question_id=question_id, comment=comment, answers_for_question=answers_for_question, actual_question=actual_question, url=url)


@app.route('/question/<question_id>/edit')
def question_edit(question_id):
    url = request.url
    actual_question = data_manager.get_question_details_sql(question_id)
    return render_template('post_form.html', question_id=question_id, actual_question=actual_question, url=url)


@app.route('/list')
def ordered_list():
    if "order_by" in request.args.keys() and "order_direction" in request.args.keys():
        aspect = request.args.get("order_by")
        if request.args.get("order_direction") == "ascending":
            ascending = True
        else:
            ascending = False
        questions = data_manager.sort_sql('question', aspect, ascending)
        return render_template('index.html', questions=questions,ascending=ascending)
    else:
        questions = data_manager.get_list_of_questions_sql()
        print ("SHOWING THE BASIC TABLE UNORDERED")
        return render_template("index.html", questions=questions)


@app.route('/question/<question_id>/vote-<vote>')
def vote_on_question(question_id, vote):
    vote_modifier = 1 if vote == 'up' else -1
    data_manager.update_vote_sql(vote_modifier, 'question', question_id)
    return redirect(request.referrer)


@app.route('/answer/<answer_id>/vote-<vote>')
def vote_on_answer(answer_id, vote):
    vote_modifier = 1 if vote == 'up' else -1
    data_manager.update_vote_sql(vote_modifier, 'answer', answer_id)
    return redirect(request.referrer)


@app.route('/question/<int:question_id>/view')
def view_count(question_id):
    data_manager.update_view_sql(question_id)
    return redirect('/question/{}'.format(question_id))


@app.route('/question/<int:question_id>/edit', methods=['POST'])
def edit_question(question_id):
    edited_question = {'title': request.form['title'], 'message': request.form['message'],
                       'submission_time': datetime.datetime.now().replace(microsecond=0), 'image': '',
                       'question_id': question_id}
    data_manager.edit_question(question_id, edited_question)
    return redirect('/question/{}'.format(question_id))


@app.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect("/")


@app.route('/<int:question_id>/answer/delete/<int:answer_id>')
def delete_answer(question_id, answer_id):
    data_manager.delete_answer(answer_id)
    return redirect('/question/{}'.format(question_id))


@app.route('/<int:question_id>/comment/<int:id>/delete')
def delete_question_comment(id, question_id):
    data_manager.delete_question_comment(id, question_id)
    return redirect('/question/{}'.format(question_id))


@app.route('/<int:question_id>/<int:answer_id>/comment/<int:id>/delete')
def delete_answer_comment(id, question_id, answer_id):
    data_manager.delete_answer_comment(id, answer_id)
    return redirect('/question/{}'.format(question_id))


@app.route('/question/<int:question_id>/comment', methods=['POST'])
def comment_question(question_id):
    comment = {'id': data_manager.generate_sql_id('comment'), 'message': request.form['question_comment'],
               'submission_time': datetime.datetime.now().replace(microsecond=0), 'edited_count': 0,
               'question_id': question_id}
    data_manager.update_question_comment(comment)
    return redirect(request.referrer)


@app.route('/question/answer/<int:answer_id>/comment', methods=['POST'])
def comment_answer(answer_id):
    comment = {'id': data_manager.generate_sql_id('comment'), 'message': request.form['answer_comment'],
               'submission_time': datetime.datetime.now().replace(microsecond=0), 'edited_count': 0,
               'answer_id': answer_id}
    print(comment)
    data_manager.update_answer_comment(comment)
    return redirect(request.referrer)


@app.route('/search')
def search():
    keyword = request.args['keyword']
    result_q = data_manager.search_by_keyword_question(keyword)
    result_a = data_manager.search_by_keyword_answer(keyword)
    return render_template('search.html', keyword_q=result_q, keyword_a=result_a)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )