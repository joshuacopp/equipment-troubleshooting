from flask import Flask, render_template, request, session, redirect, url_for
import yaml
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this!

# Load decision tree from YAML
def load_decision_tree():
    with open('decision_tree.yaml', 'r') as file:
        return yaml.safe_load(file)

decision_tree = load_decision_tree()

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
        answer_text = request.form.get('answer')
        current_q = session.get('current_question')
        
        if not answer_text or not current_q:
            return redirect(url_for('start'))
        
        # Save to history
        history = session.get('history', [])
        current_question_data = decision_tree['questions'][current_q]
        history.append({
            'question': current_question_data['text'],
            'answer': answer_text
        })
        session['history'] = history
        
        # Find the next question or conclusion
        for answer in current_question_data['answers']:
            if answer['text'] == answer_text:
                if 'next' in answer:
                    session['current_question'] = answer['next']
                    return redirect(url_for('question'))
                elif 'conclusion' in answer:
                    return redirect(url_for('conclusion', conclusion=answer['conclusion']))
        
        # Fallback if something goes wrong
        return redirect(url_for('start'))
    
    # GET request - display current question
    current_q = session.get('current_question')
    if not current_q:
        return redirect(url_for('start'))
    
    # Check if this is a conclusion instead of a question
    current_data = decision_tree['questions'].get(current_q)
    if not current_data:
        return redirect(url_for('start'))
    
    # Check if any answer leads directly to a conclusion
    for answer in current_data['answers']:
        if 'conclusion' in answer and len(current_data['answers']) == 1:
            return redirect(url_for('conclusion', conclusion=answer['conclusion']))
    
    history = session.get('history', [])
    
    return render_template('question.html', 
                         question_data=current_data,
                         history=history)

@app.route('/conclusion')
def conclusion():
    """Display the final conclusion"""
    conclusion_text = request.args.get('conclusion')
    if not conclusion_text:
        # Check if the current question has a conclusion
        current_q = session.get('current_question')
        if current_q:
            current_data = decision_tree['questions'].get(current_q)
            if current_data and 'conclusion' in current_data:
                conclusion_text = current_data['conclusion']
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
