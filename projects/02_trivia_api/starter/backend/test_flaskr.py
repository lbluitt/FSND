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
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_405_method_not_allowed_categories(self):
        response = self.client().post('/categories')
        data= json.loads(response.data)

        self.assertEqual(response.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Method not allowed')

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions']) 
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['current_category'],None)

    def test_404_invalid_questions_page(self):
        response = self.client().get('/questions?page=4000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource not found')

    def test_add_question(self):
        response=self.client().post('/questions',json={'question':'Is this a new question?','answer':'Yes!','difficulty':1,'category':1})
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])

    def test_422_question_cannot_be_inserted(self):
        #Post "difficulty" as a string and not and int to cause the insertion to fail
        response=self.client().post('/questions',json={'question':'Is this a game?','answer':'Yes!','difficulty':"this should be an int instead",'category':1})
        data=json.loads(response.data)

        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"Unprocessable")

    def test_search_question(self):
        response=self.client().post('/questions/search',json={'searchTerm':'what'})
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions']) 

    def test_405_method_not_allowed_questions_search(self):
        response = self.client().get('/questions/search?searchTerm=title')
        data= json.loads(response.data)

        self.assertEqual(response.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Method not allowed')

    def test_get_questions_by_category(self):
        response=self.client().get('/categories/1/questions')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions']) 
        self.assertTrue(data['current_category']) 

    def test_404_invalid_category(self):
        response = self.client().get('/categories/10000/questions')
        data= json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource not found')

    def test_quiz(self):
        response=self.client().post('/quizzes',json={'quiz_category':{'id':4,'type':'History'},'previous_questions':[23,5]})
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['question']))

    def test_fail_quiz_id_as_string(self):
        response=self.client().post('/quizzes',json={'quiz_category':{'id':'string','type':'History'},'previous_questions':[23,5]})
        data=json.loads(response.data)

        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'],'Unprocessable')

    def test_delete_question(self):
        response=self.client().delete('/questions/2')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['deleted'])
        

    def test_delete_inexisting_question(self):
        response=self.client().delete('/questions/2000')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'],'Unprocessable')

        








# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()