from flask import Flask, render_template_string, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "secret-key"

# -------------------------
# SUPABASE CONFIG
# -------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Survey definition
# -------------------------
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

# -------------------------
# Save to Supabase
# -------------------------
def save_to_db(answers):
    data = {
        "answers": answers
    }
    supabase.table("responses").insert(data).execute()

# -------------------------
# HTML Template
# -------------------------
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

# -------------------------
# Routes
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def survey():
    if 'current_q' not in session:
        session['current_q'] = 'q1'
        session['answers'] = {}

    current_q = session['current_q']
    question_data = SURVEY[current_q]

    if request.method == 'POST':
        # Final submit
        if 'submit' in request.form:
            save_to_db(session['answers'])
            return redirect(url_for('result'))

        answer = request.form['answer']
        session['answers'][current_q] = answer

        next_q = question_data['options'].get(answer)

        if next_q:
            session['current_q'] = next_q
        else:
            session['current_q'] = 'q4'

        return redirect(url_for('survey'))

    return render_template_string(
        TEMPLATE,
        question=question_data['question'],
        options=question_data['options'].keys(),
        answers=session.get('answers')
    )

@app.route('/result')
def result():
    return """
    <h2>Survey submitted successfully!</h2>
    <a href='/restart'>Take again</a>
    """

@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('survey'))

# Optional admin view (pull from Supabase)
@app.route('/admin')
def admin():
    response = supabase.table("responses").select("*").execute()
    return f"<pre>{response.data}</pre>"

# -------------------------
# Run app
# -------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
