from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret-key"

# Survey definition with branching logic
SURVEY = {
    "q1": {
        "question": "Do you own a car?",
        "options": {
            "yes": "q2",
            "no": "q3"
        }
    },
    "q2": {
        "question": "What brand is your car?",
        "options": {
            "toyota": "q4",
            "ford": "q4",
            "other": "q4"
        }
    },
    "q3": {
        "question": "Would you like to own a car in the future?",
        "options": {
            "yes": "q4",
            "no": "q4"
        }
    },
    "q4": {
        "question": "Review your answers and submit:",
        "options": {}
    }
}

# Save responses to SQLite
def save_to_db(answers):
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answers TEXT
        )
    ''')

    c.execute('INSERT INTO responses (answers) VALUES (?)', (str(answers),))
    conn.commit()
    conn.close()

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dynamic Survey</title>
</head>
<body>
    <h2>{{ question }}</h2>

    {% if options %}
        <form method="post">
            {% for key in options %}
                <button type="submit" name="answer" value="{{ key }}">{{ key }}</button><br><br>
            {% endfor %}
        </form>
    {% else %}
        <h3>Review your answers:</h3>
        <pre>{{ answers }}</pre>
        <form method="post">
            <button type="submit" name="submit" value="true">Submit Survey</button>
        </form>
    {% endif %}

    <br>
    <a href="/restart">Start Over</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def survey():
    if 'current_q' not in session:
        session['current_q'] = 'q1'
        session['answers'] = {}

    current_q = session['current_q']
    question_data = SURVEY[current_q]

    if request.method == 'POST':
        # Handle final submission
        if 'submit' in request.form:
            save_to_db(session['answers'])
            return redirect(url_for('result'))

        answer = request.form['answer']
        session['answers'][current_q] = answer

        # Determine next question
        next_q = question_data['options'].get(answer)

        if next_q:
            session['current_q'] = next_q
        else:
            session['current_q'] = 'q4'

        return redirect(url_for('survey'))

    return render_template_string(TEMPLATE,
                                  question=question_data['question'],
                                  options=question_data['options'].keys(),
                                  answers=session.get('answers'))

@app.route('/result')
def result():
    return """
    <h2>Survey submitted successfully!</h2>
    <a href='/restart'>Take again</a>
    """

# Restart route
@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('survey'))

# Admin route to view responses
@app.route('/admin')
def admin():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    rows = c.execute('SELECT * FROM responses').fetchall()
    conn.close()

    return f"<pre>{rows}</pre>"

if __name__ == '__main__':
    app.run(debug=True)
