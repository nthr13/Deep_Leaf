import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
import base64
from inference_sdk import InferenceHTTPClient
import tempfile
import os
import base64

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="ITyKMhMBi3HKoKsM5PrY"
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'site.db'  # Define the database file name
auth_key = "3998ee77-3ce9-4b7c-bff0-65db7106880b:fx"  # Deepl API key

def get_db():
    """Connects to the specific database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# This function initializes the database schema.
def init_db():
    """Initializes the database schema."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Flask CLI command to initialize the database
@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Executes a write query (INSERT, UPDATE, DELETE)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()

def is_logged_in():
    return 'user_id' in session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trymodel', methods=['GET', 'POST'])
def trymodel():
    if request.method == 'POST':
        print("processing Image")
        predictions_data = []
        predictions= None
        
        if 'image_file' in request.files:
                image_file = request.files['image_file']
                image_bytes = image_file.read()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                # Try passing the bytes directly for file uploads as well
                result = CLIENT.infer(image_b64, model_id="detecting-diseases/5")
                predictions = result['predictions']
    
        for prediction in predictions:
            # print(f"prediction: {prediction}")
            print(f"Disease: {prediction['class']} Confidence: {prediction['confidence']}")
            predictions_data.append({
                            'class': prediction['class'],
                            'confidence': prediction['confidence']
                        })

        return jsonify({'predictions': predictions_data})
    return render_template('try.html')

@app.route('/account')
def account():
    if is_logged_in():
        # Example: Fetch user data from the database
        user = query_db('SELECT username FROM users WHERE id = ?', (session['user_id'],), one=True)
        history = query_db('SELECT recognized_text, translated_text, target_language, timestamp FROM translation_history WHERE user_id = ? ORDER BY timestamp DESC', (session['user_id'],))
        return render_template('account.html', user=user, history=history)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = query_db('SELECT id, password FROM users WHERE username = ?', (username,), one=True)

        if user is None:
            error = 'Invalid username'
        elif user['password'] != password:  # In a real app, compare hashed passwords!
            error = 'Invalid password'

        if error is None:
            session['user_id'] = user['id']
            return redirect(url_for('account'))
        flash(error, 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif query_db('SELECT id FROM users WHERE username = ?', (username,), one=True) is not None:
            error = 'Username already exists'

        if error is None:
            execute_db('INSERT INTO users (username, password) VALUES (?, ?)', (username, password)) # In real app, hash password!
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        flash(error, 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)