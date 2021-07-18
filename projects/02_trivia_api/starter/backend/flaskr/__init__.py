import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r'*' : {"origins": '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE') 
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def get_categories():
    
    categories=Category.query.order_by(Category.id).all()

    if len(categories)==0: 
      abort(404)
    
    return jsonify({
      'success': True,
      'categories': {category.id:category.type for category in categories},
      'total_categories': len(Category.query.all())
    })

  def paginate_items(request,selection):
    page = request.args.get('page',1,type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    items = [item.format() for item in selection]

    current_items=items[start:end]

    return current_items

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def get_questions():

    try:

      questions_selection= Question.query.order_by(Question.id).all()

      #limit this to only when questions are more than 10?
      questions = paginate_items(request,questions_selection)

      if len(questions)==0:
        abort(404)

      categories_selection = Category.query.order_by(Category.id).all()

      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(Question.query.all()),
        'current_category': None,
        'categories': {category.id:category.type for category in categories_selection}

      })
    except Exception as err:
      abort(404)


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def remove_question(question_id):

    try:
      question=Question.query.filter(Question.id==question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions= paginate_items(request,selection)

      return jsonify({
        'success':True,
        'deleted': question.id
      })
    except Exception as err:
      abort(422)
      db.session.rollback()
    finally:
      db.session.close()


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions',methods=['POST'])
  def create_new_question():
    body = request.get_json()

    question = body.get('question',None)
    answer = body.get('answer',None)
    difficulty = body.get('difficulty',None)
    category = body.get('category',None)

    if question == None or question == '' or answer== None or answer=='' or difficulty==None or difficulty=='' or category==None or category=='':
        abort(422)

    try:
      question=Question(question=question,answer=answer,difficulty=difficulty,category=category)
      question.insert()
      return jsonify({
        'created':question.id,
        'success': True,
        
      })
    except Exception as err:
      abort(422)
      db.session.rollback()
    finally:
      db.session.close()



  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def search_question():
    body = request.get_json()

    search_term = body.get('searchTerm','')

    try:
      selection=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      if not selection:
        abort(404)

      current_questions=paginate_items(request,selection)

      return jsonify({
        'success': True,
        'questions':current_questions,
        'total_questions': len(selection),
        'current_category':None
      })
    except Exception as err:
      abort(422)



  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      selection_questions = Question.query.filter(Question.category==str(category_id)).all()

      if not selection_questions:
        abort(404)
      current_cuestions = paginate_items(request,selection_questions)
      category= Category.query.filter(Category.id==category_id).one_or_none()

      if not category:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_cuestions,
        'total_questions': len(Question.query.filter(Question.category==str(category_id)).all()),
        'current_category': category.type
      })
    except Exception as err:
      abort(404)



  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_question():
    body = request.get_json()
    prev_question = body.get('previous_questions',[])
    category = body.get('quiz_category',None)

    try:
      category_id = category['id'] if category['id'] else 0

      if category_id == 0:
        category_questions= Question.query.all()
      else:
        category_questions= Question.query.filter(Question.category==str(category_id)).all()

      if not category_questions:
        return abort(404)


      questions_options=[]
      for question in category_questions:
        if len(prev_question)==0:
          questions_options.append(question.format())
        if len(prev_question)>0:
          if question.id not in prev_question:
            questions_options.append(question.format())

      question=None
      if len(questions_options)>0:
          question=random.choice(questions_options) if len(questions_options)>1 else questions_options[0]

      if question:
        return jsonify({
          'success':True,
          'question':question
        })
      else:
        #if there are less than 5 questions per play for current category, once there are no more questions, will return an object without the 'question' so the frontend knows it should end the game now.
        return jsonify({
          'success':True
        })
    except Exception as err:
      abort(422)

# ERROR HANDLERS:

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':400,
      'message': 'Bad request'
    }),400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message': 'Resource not found'
    }),404

  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':422,
      'message': 'Unprocessable'
    }),422
 
  @app.errorhandler(500)
  def method_not_allowed(error):
    return jsonify({
      'success':False,
      'error':500,
      'message': 'Internal server error'
    }),500
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success':False,
      'error':405,
      'message': 'Method not allowed'
    }),405
 
  return app

    