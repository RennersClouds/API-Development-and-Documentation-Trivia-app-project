import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from settings import DB_NAME, DB_USER, DB_PASSWORD
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME
        self.database_path = "postgresql://{}:{}@{}/{}".format(
    DB_USER, DB_PASSWORD, "localhost:5432", DB_NAME
)

        # self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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
    def test_retrieve_categories(self):
        result = self.client().get('/categories/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_405_using_wrong_method_to_retrieve_categories(self):
        result = self.client().put('/categories/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_questions(self):
        result = self.client().get('/questions/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        
    
    def test_get_questions_error(self):
        result = self.client().put('/questions/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_paginated_questions_error(self):
        result = self.client().put('/questions/all?page=1000')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_delete_question(self):
        result = self.client().delete('/questions/15')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
       

    
    def test_delete_question_error(self):
        result = self.client().delete('/questions/50000')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['message'], 'bad request')

    def test_create_question(self):
        result = self.client().post('/questions/all', json={
             'question': 'questioninfo',
                'answer': 'answerinfo',
                'category' : 3,
                'difficulty': 2
        })
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
       

    def test_create_question_error(self):
        result = self.client().post('/questions/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        

    def test_search_questions(self):
        result = self.client().post('/questions/search', json={'searchTerm': 'game'})
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['current_category']))
        

    def test_search_questions_error(self):
        result = self.client().put('/questions/search', json={})
        self.assertEqual(result.status_code, 405)
       
    
    def test_get_questions_by_category(self):
        result = self.client().get('/categories/1/questions/all')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
    
    def test_get_questions_by_category_error(self):
        result = self.client().get('/categories/1000/questions/all')
        self.assertEqual(result.status_code, 405)
      
        


    def test_quizze_question(self):
        result = self.client().post('/PlayQuizzes',  json={
            "previous_questions": [5, 9], 
            "quiz_category": {'id': 1, 'type': 'Science'}
            })
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['question'])


    def test_quizze_question_error(self):
        result = self.client().post('/PlayQuizzes', json={})
        self.assertEqual(result.status_code, 400)
      
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()