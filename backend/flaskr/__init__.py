import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    paginated_data = [item.format() for item in selection]

    return paginated_data[start: end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories/all')
    def categories():
        try:
            categories = Category.query.order_by(Category.id).all()

            return jsonify({"success": True, "categories": {
                           category.id: category.type for category in categories}})

        except BaseException:
            abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
    of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions/all')
    def questions():
        # query all questions 
        questions = Question.query.all()
        categories = Category.query.all()

        paginated_questions = paginate(request, questions)

        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            "success": True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_category': "Null",
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            if question:
                return jsonify({
                    "success": True,
                    "question": question_id,
                })
            else:
                abort(405)
        except BaseException:
            abort(400)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear
    and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions/all', methods=['POST'])
    def create_question():
        info = request.get_json()
        difficultyinfo = info.get('difficulty', None)
        questioninfo = info.get('question', None)
        categoryinfo = info.get('category', None)
        answerinfo = info.get('answer', None)
        try:
            data = Question(
                question=questioninfo,
                answer=answerinfo,
                category=categoryinfo,
                difficulty=difficultyinfo)

            data.insert()

            return jsonify({
                'success': True
            })

        except BaseException:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        try:
            search = request.get_json()
            questions = Question.query.filter(
                Question.question.ilike(f'%{search["searchTerm"]}%')).all()
            paginated_search = paginate(request, questions)

            return jsonify({
                "success": True,
                'questions': paginated_search,
                'total_questions': len(questions),
                'current_category': "Null",
            })

        except BaseException:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions/all', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            categories = Category.query.get(category_id)
            questions = Question.query.filter(
                Question.category == categories.id).all()
            question = paginate(request, questions)
            return jsonify({
                "success": True,
                'questions': question,
                'total_questions': len(questions),
                'current_category': "Null",
            })
        except BaseException:
            abort(405)

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
    @app.route('/PlayQuizzes', methods=['POST'])
    def play_quizzes():

        try:

            req = request.get_json()
            prev = req['previous_questions']
            category = req['quiz_category']
            questions = Question.query.filter(
                Question.category == category['id']).all()
            formatted_questions = [question.format() for question in questions]

            newQeestionss = []

            for q in formatted_questions:
                if q['id'] not in prev:
                    newQeestionss.append(q)

            if len(newQeestionss) == 0:
                return jsonify({
                    'success': True
                })
            else:
                rand = random.choice(newQeestionss)

            return jsonify({
                'question': rand
            })

        except BaseException:
            abort(400)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):

        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_found(error):

        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):

        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server errors'
        }), 500

    return app
