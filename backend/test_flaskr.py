import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # def test_retrieve_categories(self):
    #     # Test get categories
    #     result = self.client().get('/categories')
    #     data = json.loads(result.data)
    #     self.assertEqual(result.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['categories'])

    # def test_405_using_wrong_method_to_retrieve_categories(self):
    #     result = self.client().patch('/categories')
    #     data = json.loads(result.data)
    #     self.assertEqual(result.status_code, 405)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'method not allowed')

    def test_retrieve_questions(self):
        result = self.client().get('/questions/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 19)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
    
    def test_retrieve_questions_error(self):
        result = self.client().patch('/questions/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_delete_question(self):
        result = self.client().delete('/questions/4')
        data = json.loads(result.data)
        question = Question.query.filter(Question.id == 4).one_or_none()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)
    
    def test_delete_question_error(self):
        result = self.client().delete('/questions/50000')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):
        result = self.client().post('/questions', json=self.new_question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_question_error(self):
        result = self.client().post('/questions/1', json=self.new_question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_search_questions(self):
        result = self.client().post('/questions/search', json={'searchTerm': 'pyramid'})
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['current_category']))
        self.assertTrue(data['total_questions'])

    def test_search_questions_error(self):
        result = self.client().post('/questions/search', json={'searchTerm': 'nflsdjljsf'})
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(len(data['current_category']), 0)
        self.assertEqual(data['total_questions'], 0)
    
    def test_get_questions_by_category(self):
        result = self.client().get('/categories/1/questions')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(data['total_questions'])

    def test_test_get_questions_by_category_error(self):
        result = self.client().post('/categories/1/questions')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_quizze_question(self):
        result = self.client().post('/quizzes',  json={"previous_questions": [], "quiz_category": {'id': 1, 'type': 'Science'}})
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))

    def test_quizze_question_error(self):
        result = self.client().post('/quizzes', json={"previous_questions": [], "quiz_category": {'id': 10, 'type': 'Economic'}})
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()