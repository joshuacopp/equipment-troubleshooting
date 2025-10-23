from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
from models import db, Question, Answer

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production-please')

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Admin credentials - change these!
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/start', methods=['GET'])
def start():
    """Start a new troubleshooting session"""
    session.clear()
    session['history'] = []
    session['current_question'] = 'start'
    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    """Display current question and handle answers"""
    
    if request.method == 'POST':
        # Get the selected answer
        answer_id = request.form.get('answer_id')
        current_q_id = session.get('current_question')
        
        if not answer_id or not current_q_id:
            return redirect(url_for('start'))
        
        # Get answer from database
        answer = Answer.query.get(answer_id)
        if not answer:
            return redirect(url_for('start'))
        
        # Save to history
        history = session.get('history', [])
        current_question = Question.query.filter_by(question_id=current_q_id).first()
        history.append({
            'question': current_question.text,
            'answer': answer.text
        })
        session['history'] = history
        
        # Check if this answer leads to next question or conclusion
        if answer.next_question_id:
            session['current_question'] = answer.next_question_id
            return redirect(url_for('question'))
        elif answer.conclusion:
            return redirect(url_for('conclusion', conclusion=answer.conclusion))
        else:
            # No next question and no conclusion - error state
            flash('Configuration error: answer has no next step')
            return redirect(url_for('start'))
    
    # GET request - display current question
    current_q_id = session.get('current_question')
    if not current_q_id:
        return redirect(url_for('start'))
    
    # Get question from database
    current_question = Question.query.filter_by(question_id=current_q_id).first()
    if not current_question:
        flash(f'Question "{current_q_id}" not found in database')
        return redirect(url_for('start'))
    
    # Get answers for this question
    answers = Answer.query.filter_by(question_id=current_question.id).order_by(Answer.order).all()
    
    history = session.get('history', [])
    
    return render_template('question.html', 
                         question=current_question,
                         answers=answers,
                         history=history)

@app.route('/conclusion')
def conclusion():
    """Display the final conclusion"""
    conclusion_text = request.args.get('conclusion')
    
    if not conclusion_text:
        return redirect(url_for('start'))
    
    history = session.get('history', [])
    
    return render_template('conclusion.html', 
                         conclusion=conclusion_text,
                         history=history)

@app.route('/restart')
def restart():
    """Restart the troubleshooting process"""
    return redirect(url_for('start'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

def admin_required(f):
    """Decorator to require admin login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access admin area', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    questions = Question.query.order_by(Question.category, Question.question_id).all()
    return render_template('admin_dashboard.html', questions=questions)

@app.route('/admin/question/add', methods=['GET', 'POST'])
@admin_required
def admin_add_question():
    """Add new question"""
    if request.method == 'POST':
        question_id = request.form.get('question_id')
        text = request.form.get('text')
        category = request.form.get('category', '')
        
        # Check if question_id already exists
        existing = Question.query.filter_by(question_id=question_id).first()
        if existing:
            flash(f'Question ID "{question_id}" already exists', 'error')
            return redirect(url_for('admin_add_question'))
        
        question = Question(
            question_id=question_id,
            text=text,
            category=category
        )
        db.session.add(question)
        db.session.commit()
        
        flash(f'Question "{question_id}" added successfully', 'success')
        return redirect(url_for('admin_edit_question', id=question.id))
    
    return render_template('admin_question_form.html', question=None)

@app.route('/admin/question/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_question(id):
    """Edit question and its answers"""
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question.question_id = request.form.get('question_id')
        question.text = request.form.get('text')
        question.category = request.form.get('category', '')
        db.session.commit()
        flash('Question updated successfully', 'success')
        return redirect(url_for('admin_edit_question', id=id))
    
    answers = Answer.query.filter_by(question_id=id).order_by(Answer.order).all()
    all_questions = Question.query.order_by(Question.question_id).all()
    
    return render_template('admin_question_form.html', 
                         question=question, 
                         answers=answers,
                         all_questions=all_questions)

@app.route('/admin/question/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_question(id):
    """Delete question"""
    question = Question.query.get_or_404(id)
    
    # Delete all answers for this question
    Answer.query.filter_by(question_id=id).delete()
    
    # Delete the question
    db.session.delete(question)
    db.session.commit()
    
    flash(f'Question "{question.question_id}" deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/answer/add/<int:question_id>', methods=['POST'])
@admin_required
def admin_add_answer(question_id):
    """Add answer to question"""
    question = Question.query.get_or_404(question_id)
    
    text = request.form.get('text')
    next_question_id = request.form.get('next_question_id') or None
    conclusion = request.form.get('conclusion') or None
    
    # Get the highest order number for this question
    max_order = db.session.query(db.func.max(Answer.order)).filter_by(question_id=question_id).scalar() or 0
    
    answer = Answer(
        question_id=question_id,
        text=text,
        next_question_id=next_question_id,
        conclusion=conclusion,
        order=max_order + 1
    )
    db.session.add(answer)
    db.session.commit()
    
    flash('Answer added successfully', 'success')
    return redirect(url_for('admin_edit_question', id=question_id))

@app.route('/admin/answer/<int:id>/edit', methods=['POST'])
@admin_required
def admin_edit_answer(id):
    """Edit answer"""
    answer = Answer.query.get_or_404(id)
    
    answer.text = request.form.get('text')
    answer.next_question_id = request.form.get('next_question_id') or None
    answer.conclusion = request.form.get('conclusion') or None
    
    db.session.commit()
    
    flash('Answer updated successfully', 'success')
    return redirect(url_for('admin_edit_question', id=answer.question_id))

@app.route('/admin/answer/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_answer(id):
    """Delete answer"""
    answer = Answer.query.get_or_404(id)
    question_id = answer.question_id
    
    db.session.delete(answer)
    db.session.commit()
    
    flash('Answer deleted successfully', 'success')
    return redirect(url_for('admin_edit_question', id=question_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
