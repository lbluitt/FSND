
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movie, Actor

class CastingAgencyTestCase(unittest.TestCase):

    def setUp(self):
        self.app=create_app()
        self.client= self.app.test_client
        self.database_name = "casting-agency-test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app,self.database_path)

        # users
        self.casting_assistant = os.environ.get('CASTING_ASSISTANT')
        self.casting_director = os.environ.get('CASTING_DIRECTOR')
        self.executive_producer = os.environ.get('EXECUTIVE_PRODUCER')

        #bind app to current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        pass


    # Get actors 

    def test_get_actors(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().get('/actors',headers=headers)
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['actors']))

    def test_get_actors_now_allowed(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().get('/actors/1',headers=headers)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertTrue(data['message'],'Method not allowed')

    # Get movies

    def test_get_movies(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().get('/movies',headers=headers)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['movies']))
    
    def test_get_movies_not_allowed(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().get('/movies/1',headers=headers)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertTrue(data['message'],'Method not allowed')

    # Delete Actors
    
        # def test_delete_actor(self):
    #     headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
    #     response=self.client().delete('/actors/2',headers=headers)
    #     data=json.loads(response.data)

    #     self.assertEqual(response.status_code,200)
    #     self.assertEqual(data['success'],True)
    #     self.assertTrue(data['deleted'])


    def test_delete_actor_unprocessable(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().delete('/actors/3200',headers=headers)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertTrue(data['message'],'Unprocessable')

    #Delete movies

    # def test_delete_movie(self):
    #     headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
    #     response=self.client().delete('/movies/2',headers=headers)
    #     data=json.loads(response.data)

    #     self.assertEqual(response.status_code,200)
    #     self.assertEqual(data['success'],True)
    #     self.assertTrue(data['deleted'])

    def test_delete_movies_unprocessable(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().delete('/movies/3200',headers=headers)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertEqual(data['message'],'Unprocessable')

    # Post actors

    def test_post_actors(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().post('/actors',json={'name':'Luke','birthdate':'8-8-1960','gender':'M'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])

    def test_post_actors_missing_name(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().post('/actors',json={'birthdate':'8-8-1960','gender':'M'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertEqual(data['message'],'Unprocessable')


    # Post movies

    def test_post_movies(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().post('/movies',json={'title':'Where is the keyboard?','release_date':'8-8-1960'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])

    def test_post_movies_unprocessable_by_endpoint(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().post('/movies/23',json={'title':'Where is the keyboard?','release_date':'8-8-1960'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'Method not allowed')

    #Patch actors

    def test_patch_actors(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().patch('/actors/4',json={'name':'Alefo'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['actors']))

    def test_patch_actors_inexisting_index(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().patch('/actors/4000',json={'name':'Alefo'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertTrue(data['message'],'Unprocessable')

    #Patch movies

    def test_patch_movies(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().patch('/movies/4',json={'title':'hidden letter'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['movies']))

    def test_patch_movies_inexisting_index(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().patch('/movies/4000',json={'name':'Alefo'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertTrue(data['message'],'Unprocessable')

    #RBAC tests

    #Casting assistant
    def test_get_movies_casting_assistant(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.casting_assistant}
        response=self.client().get('/movies',headers=headers)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['movies']))

    def test_get_movies_casting_assistant(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.casting_assistant}
        response=self.client().post('/actors',json={'name':'Luke','birthdate':'8-8-1960','gender':'M'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,403)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'permission not found')

    #Casting director
    def test_post_actor_casting_director(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.casting_director}
        response=self.client().post('/actors',json={'name':'Luke','birthdate':'8-8-1960','gender':'M'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])

    def test_post_movies_casting_director_unauthorized(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.casting_director}
        response=self.client().post('/movies',json={'title':'Where is the keyboard?','release_date':'8-8-1960'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,403)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'permission not found')

    #executive producer
    def test_post_actor_executive_director(self):
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer}
        response=self.client().post('/actors',json={'name':'Luke','birthdate':'8-8-1960','gender':'M'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])

    def test_post_movies_casting_director_bad_request(self): #added dash before bearer token to cause a bad request
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self.executive_producer+"-"}
        response=self.client().post('/movies',json={'title':'Where is the keyboard?','release_date':'8-8-1960'},headers=headers)
        
        data=json.loads(response.data)
        self.assertEqual(response.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Unable to parse authentication token.')


if __name__=='__main__':
    unittest.main()