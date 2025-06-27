from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os # Import the os module

from flask import abort




# --- Flask App Configuration ---
app = Flask(__name__)

# Define the base directory of your application
basedir = os.path.abspath(os.path.dirname(__file__))
#const port = process.env.PORT || 4000
# Configure SQLite database using an absolute path
# The database file will be created inside the 'instance' folder within your app's root directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable tracking modifications overhead

db = SQLAlchemy(app)

# Ensure the instance folder exists before trying to create the database file
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# --- Database Model ---
class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    amount_ml = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # When the record was created/updated

    def __repr__(self):
        return f'<Feed {self.id}: {self.start_time.strftime("%d/%m/%y %H:%M")} - {self.end_time.strftime("%d/%m/%y %H:%M")} ({self.amount_ml}ml)>'

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        # Handle form submission to add a new feed
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        amount_ml = request.form['amount_ml']
        
        try:
            # Convert string to datetime object
            # Note: datetime-local input format is 'YYYY-MM-DDTHH:MM'
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            amount_ml = float(amount_ml)

            new_feed = Feed(start_time=start_time, end_time=end_time, amount_ml=amount_ml)
            db.session.add(new_feed)
            db.session.commit()
            return redirect(url_for('index')) # Redirect to prevent re-submission on refresh
        except (ValueError, KeyError) as e:
            # Handle invalid input gracefully (e.g., show an error message)
            print(f"Error processing form: {e}")
            # In a real app, you might want to flash a message to the user:
            # flash(f"Error adding feed: {e}", "error")
            pass

    # Display existing feeds
    # Order by start_time descending to show latest feeds first
    feeds = Feed.query.order_by(Feed.start_time.desc()).all()
    key = request.args.get('key')
    key = request.form.get('key')
    # Insert this line at the top of your Flask app, after importing necessary modules:
    #if request.form.get('key') == 'gghdsbzu': return render_template('index.html', feeds=feeds)
    #if request.args.get('key') == 'gghdsbzu': return render_template('index.html', feeds=feeds)
    return render_template('index.html', feeds=feeds, key=key)
# --- Database Initialization ---
# This block ensures the database and tables are created when the app runs for the first time
# It must be within an app_context() to interact with Flask-SQLAlchemy
with app.app_context():
    db.create_all()

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0",  port=10000) # debug=True for development, turn off for production
