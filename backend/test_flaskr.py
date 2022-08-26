import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_USER")}@localhost:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        db.init_app(self.app)
        # create all tables
        db.create_all()

            
    
    def tearDown(self):
        """Executed after reach test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_headers(self):
        return {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

    def test_categories(self):

        category = Category(type="Music")
        db.session.add(category)
        db.session.commit()

        response = self.client.get("/categories", headers=self.get_headers())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

        body = response.get_json()

        categories = body.get("categories")


        self.assertEqual(categories.get("1"), "Music")

    def test_get_questions_by_category(self):
        category = Category(type="Music")
        db.session.add(category)
        db.session.commit()

        category_id = category.id

        question = Question(question="Who won the 2021 grammy awards?", answer="Taylor Swift,", difficulty=1, category=category_id)
        db.session.add(question)
        db.session.commit()

        response = self.client.get(f"/categories/{category_id}/questions", headers=self.get_headers())

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        questions = body.get("questions")
        total_questions = body.get("totalQuestions")
        current_category = body.get("currentCategory")

        self.assertEqual(len(questions), 1)
        self.assertEqual(total_questions, 1)
        self.assertEqual(current_category, category.type)

    def test_get_questions_by_invalid_category(self):
        

        response = self.client.get("/categories/500/questions", headers=self.get_headers())

        self.assertEqual(response.status_code, 404)

        body = response.get_json()
        error = body.get("error")
        self.assertEqual(error, "not found")

    
    def test_add_new_question(self):

        category = Category(type="Music")
        db.session.add(category)
        db.session.commit()


        new_question = json.dumps({
            "question": "Who won the 2021 grammy awards?", 
            "answer":"Taylor Swift",
            "difficulty": 1,
            "category": category.id
        })

        response = self.client.post("/questions", headers=self.get_headers(), data=new_question)
        self.assertEqual(response.status_code, 201)
        
        body = response.get_json()

        question =  body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')

        self.assertEqual(question, "Who won the 2021 grammy awards?")
        self.assertEqual(answer, "Taylor Swift")
        self.assertEqual(difficulty, 1)

    def test_delete_question(self):
        category = Category(type="Music")
        db.session.add(category)
        db.session.commit()

        category_id = category.id

        question = Question(question="Who won the 2021 grammy awards?", answer="Taylor Swift,", difficulty=1, category=category_id)
        db.session.add(question)
        db.session.commit()

        question_id = question.id


        response = self.client.delete(f"/questions/{question_id}", headers=self.get_headers())

        self.assertEqual(response.status_code, 200)

        body = response.get_json()


        message = body.get('success')

        self.assertEqual(message, "Question deleted successfully")





 






    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()