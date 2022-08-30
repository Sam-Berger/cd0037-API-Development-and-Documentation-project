import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTION"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        category_dictionary = {}
        for category in categories:
            category_dictionary[category.id] = category.type

        json = {"categories": category_dictionary, "success": True}
        return jsonify(json)

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
        questions_per_page = 10
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * questions_per_page
        end = start + questions_per_page
        questions_query = Question.query.all()
        if questions_query is None:
            abort(404)
        questions = [question.format() for question in questions_query]
        current_questions = questions[start:end]

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.all()
        category_dictionary = {}
        for category in categories:
            category_dictionary[category.id] = category.type


        questions = Question.query.all()
        return jsonify({
            "questions": current_questions,
            "totalQuestions": len(questions),
            "categories": category_dictionary,
            "current_category": "",
            "success": True
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods = ["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)
        try:
            if search:
                questions_query = Question.query.filter(
                    Question.question.ilike("%{}%".format(search))
                )
                questions = [question.format() for question in questions_query]


                return jsonify(
                    {
                        "questions": questions,
                        "success": True,
                    }
                )

            else:
                new_question_object = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                new_question_object.insert()

                return jsonify(
                    {
                        "success": True,
                        "created": new_question_object.id,
                    }
                )

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    Done, above in create_question

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.


    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        category_id_str = str(category_id)
        questions_query = Question.query.filter(Question.category == category_id_str).all()
        questions = [question.format() for question in questions_query]

        return jsonify(
            {
                "success": True,
                "questions": questions
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
    @app.route("/quizzes", methods = ["POST"])
    def play_quiz():
        try:
            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']['id']
            if (quiz_category == 0):
                questions_query = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions_query = Question.query.filter(Question.category == quiz_category, Question.id.notin_(previous_questions)).all()

            max = len(questions_query)-1
            if max >= 0:
                question = questions_query[random.randint(0, max)].format()
            else:
                question = False

            return jsonify(
                {
                    "success": True,
                    "question": question
                }
            )
        except:
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
    return app

