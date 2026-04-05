from flask import Flask, render_template_string, request, redirect, url_for, session

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
        "question": "Thank you! Submit survey?",
        "options": {}
    }
}

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dynamic Survey</title>
</head>
<body>
    <h2>{{ question }}</h2>
    <form method="post">
        {% for key in options %}
            <button type="submit" name="answer" value="{{ key }}">{{ key }}</button><br><br>
        {% endfor %}
    </form>
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
        answer = request.form['answer']
        session['answers'][current_q] = answer

        # Determine next question
        next_q = question_data['options'].get(answer)

        if next_q:
            session['current_q'] = next_q
        else:
            return redirect(url_for('result'))

        return redirect(url_for('survey'))

    return render_template_string(TEMPLATE,
                                  question=question_data['question'],
                                  options=question_data['options'].keys())

@app.route('/result')
def result():
    answers = session.get('answers', {})
    return f"""
    <h2>Survey Complete</h2>
    <pre>{answers}</pre>
    <a href='/restart'>Restart Survey</a>
    """

# NEW: Restart route
@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('survey'))

if __name__ == '__main__':
    app.run(debug=True)
