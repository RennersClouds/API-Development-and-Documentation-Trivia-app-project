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
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories/all')
    def categories():

        categories = Category.query.all()
        formated_category = [category.format() for category in categories]
        return jsonify({
            "success": True,
            "categories": formated_category
        })


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
    @app.route('/questions/all')
    def questions():
        categories = Category.query.all()
        formated_category = [category.format() for category in categories]

        questions = Question.query.all()
        paginated_questions = paginate(request, questions)

        if not len(paginated_questions):
            abort(404)

        return jsonify({
            'success': True,
            'question': paginated_questions,
            'category': formated_category,
            'total questions': len(paginated_questions)
            })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete(question_id):

        question = Question.query.get(question_id)
        delete(question)
        # delete(question.id)
        if question:
            return jsonify({
                "success": True,
            })
        else:
            abort(405)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            sent = request.get_json()
            difficulty = int(sent.get('difficulty', None))
            question = sent.get('question', None)
            category = int(sent.get('category', None))
            answer = sent.get('answer', None)
            data = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            data.insert()

            return jsonify({
                   'success': True
                   })

        except:
             abort(405)
       


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
            search_term = request.get_json()
            search_word = format(search_term.lower())
            results ={}
            results = Question.query.filter(Question.category).filter(Question.question.ilike('%{}%'.format(search_word))).all()
            formatted_results = [result.format()for result in results]
          
            return jsonify({
               'success': True,
                    "questions": formatted_results,
                    "totalQuestions": len(results),
                    "currentCategory": formatted_results.category
                 })

        except:
            abort(422)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            question = Question.query.filter(Question.category == category_id).all()
            # questions = paginate(request, question)
      
            return jsonify({
                'success': True,
                'current_category': category_id,
                'questions': question,
                'totalQuestions': len(question)
             })  
        except:
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
        # body = request.get_json()
        previous_questions = request.get_json('previous_questions', '')
        quiz_category = request.get_json('quiz_category', '')

        questions_list = []

        try:
            if quiz_category['id'] == 0:
                questions = Question.query.all()

            else:
                questions = Question.query.filter_by(category=str(quiz_category)).all()
            
            for question in questions:
                if question.id not in previous_questions:
                    questions_list.append(question)

            if len(questions_list) == 0:
                return jsonify({
                    'success': False,
                    'question': False
                })
            else:
                return jsonify({
                    'success': True,
                    'question': random.choice(questions_list)
                })
        except:
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

