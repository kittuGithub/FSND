import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

ITEMS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app)
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    return response
  
  @app.route('/categories')
  def get_categories():
    try:
      # Get the categories
      categories = Category.query.all()

      #Get the Categories list
      categoriesList = {}
      for category in categories:
        categoriesList[category.id] = category.type

      return jsonify({
        'Success': True,
        'categories': categoriesList
      })
    except:
      abort(422)

  @app.route('/questions')
  def get_quesions():
    try:
      # Get the questions
      questionsSelected = Question.query.all()
      # Get the categories
      categories = Category.query.all()

      #Get the Categories list
      categoriesList = {}
      for category in categories:
        categoriesList[category.id] = category.type

      return jsonify({
        'Success': True,
        'total_questions': len(questionsSelected),
        'categories': categoriesList,
        'questions': questions_paginate(request, questionsSelected)
      })
    except:
       abort(422)
  
  @app.route("/questions/<question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
        #pass the question_id to get the question referrence to delete it
        question = Question.query.get(question_id)
        question.delete()
        return jsonify({
            'Success': True,
            'deleted': question_id,
            'message': "Successfully deleted the question"
        })
    except:
        abort(422)

  @app.route("/questions", methods=['POST'])
  def create_question():
    try:
      #Get the complete request of payload 
      payload = request.get_json()

      #Get all the properties required to create a question from the payload
      question = payload.get('question')
      answer = payload.get('answer')
      difficulty = payload.get('difficulty')
      category = payload.get('category')

      # create the question object instace to store in the DB
      question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

      #Insert the question
      question.insert()

      return jsonify({
          'Success': True,
          'created': question.id,
          'message': "Successfully created a question"
      })
    except:
        abort(422)

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      #Get the complete request of payload 
      payload = request.get_json()
      #Get the search item from payload 
      searchTerm = payload.get('searchTerm')
      print("THe searchTerm is ", searchTerm)
      
      if searchTerm:
        #Filter the questions based on search item 
        searchKeyword = "%{}%".format(searchTerm)
        searchedResults = Question.query.filter(Question.question.ilike(searchKeyword)).all()
      
      print("The searched results are ::: ", searchedResults)

      #Format the search Items
      searchList = []
      for searchItem in searchedResults:
        searchList.append(searchItem.format())

      return jsonify({
          'Success': True,
          'questions': searchList,
          'total_questions': len(searchList)
      })
    except:
      abort(422)

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      print("Category id :::: ", category_id)
      # Pass the category_id to filter the Questions based on category
      questions = Question.query.filter_by(category=category_id).all()

      print("QUestion are ::: ", questions)

      #Format the filter Items
      questionsList = []
      for questionItem in questions:
        questionsList.append(questionItem.format())

      return jsonify({
          'Success': True,
          'total_questions': len(questionsList),
          'questions': questionsList,
          'current_category': category_id
      })
    except:
      abort(404)


  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      #Get the complete request of payload 
      payload = request.get_json()
      #Get the category from payload 
      category = payload.get('quiz_category')
      #Get the previous questions from payload 
      previousQuestions = payload.get('previous_questions')
      #Retrieve the categoryId
      categoryId = category.get('id')
      print("previousQuestions::::: ", previousQuestions)

      if category['type'] == 'click':
        questions = Question.query.all()
      else:
        questions = Question.query.filter_by(category=categoryId).all()
      
      print("the filtered questions are ", questions, len(questions))
      availableQuestions = []

      for availQuestion in questions:
        if availQuestion.id not in previousQuestions:
          availableQuestions.append(availQuestion)
      
      print("The available questions out of all filtered questions are ::: ", availableQuestions, len(availableQuestions))
      
      if(len(availableQuestions) > 0):
        randomQuestion = random.choice(availableQuestions).format()
      else:
        randomQuestion = False

      print("the random question is :::: ", randomQuestion)
      return jsonify({
          'Success': True,
          'question': randomQuestion
      })
    except:
      abort(422)

 
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "Success": False,
        "error": 400,
        "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": 'unprocessable'
    }), 422


  def questions_paginate(request, questions_selected):
    page = request.args.get('page', 1, type=int)
    startPage = (page - 1) * ITEMS_PER_PAGE
    endPage = startPage + ITEMS_PER_PAGE
    questionsSelectedList = []
      for questionItem in questions_selected:
        questionsSelectedList.append(questionItem.format())
    questions = questionsSelectedList
    current_questions = questions[startPage:endPage]
    return current_questions
  
  return app

    