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
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "postgres", "localhost:5432", self.database_name
)
        
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "What is the capitol of Missouri?",
            "answer": "Jefferson City",
            "difficulty": 1,
            "category": "3"
        }

        self.new_question_422 = {
            "question": "What is the capitol of Missouri?",
            "answer": "Jefferson City",
            "difficulty": "asdasd",
            "category": "3"
        }

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
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_get_questions_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "boxer"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # Even if there are no results, we don't need to throw an error. It should find nothing, so I want to throw a 200
    def test_get_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "dkhfslfhaslkdjgf"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json=self.new_question_422)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)


    def test_delete_question(self):
        test_question = Question(question="new_question", answer="new_answer", category=1, difficulty=1)
        test_question.insert()
        test_question_id = test_question.id

        res = self.client().delete(f'/questions/{test_question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == test_question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], test_question_id)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_get_questions_by__nonexistent_category(self):
        res = self.client().get("/categories/30000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
    
    def test_quiz(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {
                "type": "Science",
                "id": "1"
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()