from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
from models import db, Question, Answer, TroubleshootingSession
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Admin credentials from environment variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

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
    
    # Create new session tracking
    session_id = str(uuid.uuid4())
    session['tracking_id'] = session_id
    
    # Create database record
    new_session = TroubleshootingSession(
        session_id=session_id,
        started_at=datetime.utcnow(),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )
    db.session.add(new_session)
    db.session.commit()
    
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
    
    # Update session tracking
    tracking_id = session.get('tracking_id')
    if tracking_id:
        tracking_session = TroubleshootingSession.query.filter_by(session_id=tracking_id).first()
        if tracking_session:
            tracking_session.completed_at = datetime.utcnow()
            tracking_session.path_taken = history
            tracking_session.conclusion_reached = conclusion_text
            tracking_session.abandoned = False
            db.session.commit()
    
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
    # Sort by category first, then by question_id alphabetically
    questions = Question.query.order_by(
        Question.category.asc().nullsfirst(),
        Question.question_id.asc()
    ).all()
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
    
    # Sort answers by order
    answers = Answer.query.filter_by(question_id=id).order_by(Answer.order.asc()).all()
    all_questions = Question.query.order_by(Question.question_id.asc()).all()
    
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

@app.route('/admin/answer/<int:id>/move-up', methods=['POST'])
@admin_required
def admin_move_answer_up(id):
    """Move answer up in order"""
    answer = Answer.query.get_or_404(id)
    
    # Find answer above this one
    answer_above = Answer.query.filter(
        Answer.question_id == answer.question_id,
        Answer.order < answer.order
    ).order_by(Answer.order.desc()).first()
    
    if answer_above:
        # Swap orders
        answer.order, answer_above.order = answer_above.order, answer.order
        db.session.commit()
        flash('Answer moved up', 'success')
    else:
        flash('Answer is already at the top', 'error')
    
    return redirect(url_for('admin_edit_question', id=answer.question_id))

@app.route('/admin/answer/<int:id>/move-down', methods=['POST'])
@admin_required
def admin_move_answer_down(id):
    """Move answer down in order"""
    answer = Answer.query.get_or_404(id)
    
    # Find answer below this one
    answer_below = Answer.query.filter(
        Answer.question_id == answer.question_id,
        Answer.order > answer.order
    ).order_by(Answer.order.asc()).first()
    
    if answer_below:
        # Swap orders
        answer.order, answer_below.order = answer_below.order, answer.order
        db.session.commit()
        flash('Answer moved down', 'success')
    else:
        flash('Answer is already at the bottom', 'error')
    
    return redirect(url_for('admin_edit_question', id=answer.question_id))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Analytics dashboard"""
    from sqlalchemy import func
    
    # Total sessions
    total_sessions = TroubleshootingSession.query.count()
    completed_sessions = TroubleshootingSession.query.filter_by(abandoned=False).count()
    abandoned_sessions = TroubleshootingSession.query.filter_by(abandoned=True).count()
    
    # Most common conclusions
    conclusion_stats = db.session.query(
        TroubleshootingSession.conclusion_reached,
        func.count(TroubleshootingSession.id).label('count')
    ).filter(
        TroubleshootingSession.conclusion_reached.isnot(None)
    ).group_by(
        TroubleshootingSession.conclusion_reached
    ).order_by(
        func.count(TroubleshootingSession.id).desc()
    ).limit(10).all()
    
    # Recent sessions
    recent_sessions = TroubleshootingSession.query.order_by(
        TroubleshootingSession.started_at.desc()
    ).limit(20).all()
    
    # Average questions per session
    avg_questions = db.session.query(
        func.avg(func.json_array_length(TroubleshootingSession.path_taken))
    ).filter(
        TroubleshootingSession.path_taken.isnot(None)
    ).scalar() or 0
    
    return render_template('admin_analytics.html',
                         total_sessions=total_sessions,
                         completed_sessions=completed_sessions,
                         abandoned_sessions=abandoned_sessions,
                         conclusion_stats=conclusion_stats,
                         recent_sessions=recent_sessions,
                         avg_questions=round(avg_questions, 1))

@app.route('/admin/session/<session_id>')
@admin_required
def admin_view_session(session_id):
    """View detailed session information"""
    session_record = TroubleshootingSession.query.filter_by(session_id=session_id).first_or_404()
    return render_template('admin_session_detail.html', session=session_record)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)