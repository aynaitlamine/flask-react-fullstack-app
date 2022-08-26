import json
import os
from flask import Flask, request, abort, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.sql.expression import cast

from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS(app, origins="*")
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):

        response.headers.add("Access-Control-Allow", '*')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        return jsonify({ 'categories': { category.id: category.type for category in categories}})


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def get_questions():
        page = request.args.get('page', 1, type=int)
        pagination = Question.query.paginate(page, per_page=QUESTIONS_PER_PAGE, error_out=False)
        questions = pagination.items
        categories = Category.query.all()
        prev_page = None
        
        if pagination.has_prev :
            prev_page = url_for('.get_questions', page=page -1 )

        next_page = None
        if pagination.has_next:
            next_page = url_for('.get_questions', page=page + 1 )

        

        return jsonify({ 
            'questions': [question.format() for question in questions],
            'total_questions': pagination.total,
            'categories': { category.id: category.type for category in categories}
            
            }), 200
    
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        question = Question.query.get_or_404(id)
        try:
            question.delete()
            return jsonify({
                'success': 'Question deleted successfully',
            }), 200
        except: 
            abort('422')

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json();

        question = body.get('question',None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        
        if (question, answer, category, difficulty)  is None :
            abort(400)

        try:
            new_question = Question(question, answer, category, difficulty)
            new_question.insert()
            return jsonify({
                'question':  question,
                'answer':  answer,
                'difficulty': difficulty,
                'category': category,
            }), 201

        except:
            abort(422)


        

        

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def questions_search():

        body = request.get_json();
        search_term = body.get('searchTerm', None)
        if search_term is None and search_term == '':
            abort(400)

        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        return  jsonify({
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions")
    def get_questions_by_category(id):

        current_category = Category.query.get_or_404(id)

        questions = Question.query.filter(cast(Question.category, sqlalchemy.Integer)==current_category.id).all()
        
        return jsonify(
            { 
            'questions': [ question.format() for question in questions],
            'totalQuestions': len(questions),
            'currentCategory': current_category.type
            }
        )
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def play():

        body = request.get_json()

        quiz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')

        category_type, category_id = quiz_category.values()

        questions = None
        next_question = None

        if category_id != 0:
            questions = Question.query.filter(cast(Question.category, sqlalchemy.Integer) == category_id).filter(Question.id.notin_((previous_questions))).all()

        else:
            questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
                
        
        if len(questions) > 0:
            next_question = random.choice(questions).format()

        return jsonify({
            'question' : next_question
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(e):
        response = jsonify({ 'error' : 'not found'})
        response.status_code = 404

        return response


    @app.errorhandler(422)
    def unprocessed_request(e):
        response = jsonify({ 'error' : 'unable to process your request'})
        response.status_code = 422

        return response


    @app.errorhandler(400)
    def bad_request(e):
        response = jsonify({ 'error' : 'bad request'})
        response.status_code = '400'

        return response



    @app.before_request
    def before_request():
        if not request.accept_mimetypes.accept_json:
            abort(400)

        
        





    return app

