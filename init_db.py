"""
Database initialization and YAML migration script
Run this once to set up your database and import existing YAML data
"""

import os
import yaml
from app import app, db
from models import Question, Answer

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")

def migrate_yaml_to_db(yaml_file='decision_tree.yaml'):
    """Migrate data from YAML file to database"""
    
    if not os.path.exists(yaml_file):
        print(f"✗ YAML file '{yaml_file}' not found")
        return
    
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    with app.app_context():
        # Clear existing data
        Answer.query.delete()
        Question.query.delete()
        db.session.commit()
        print("✓ Cleared existing database data")
        
        questions_data = data.get('questions', {})
        question_map = {}  # Maps question_id to Question object
        
        # First pass: Create all questions
        for q_id, q_data in questions_data.items():
            question = Question(
                question_id=q_id,
                text=q_data['text'],
                category=''  # You can add categories later
            )
            db.session.add(question)
            question_map[q_id] = question
        
        db.session.commit()
        print(f"✓ Created {len(questions_data)} questions")
        
        # Second pass: Create all answers
        answer_count = 0
        for q_id, q_data in questions_data.items():
            question_obj = question_map[q_id]
            
            for idx, answer_data in enumerate(q_data.get('answers', [])):
                answer = Answer(
                    question_id=question_obj.id,
                    text=answer_data['text'],
                    next_question_id=answer_data.get('next'),
                    conclusion=answer_data.get('conclusion'),
                    order=idx + 1
                )
                db.session.add(answer)
                answer_count += 1
        
        db.session.commit()
        print(f"✓ Created {answer_count} answers")
        print("\n✅ Migration complete!")
        print(f"   Questions: {len(questions_data)}")
        print(f"   Answers: {answer_count}")

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    
    print("\nMigrating YAML data to database...")
    migrate_yaml_to_db()
    
    print("\n" + "="*50)
    print("Setup complete! Your database is ready to use.")
    print("="*50)