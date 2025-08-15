# Import required libraries
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Configure the SQLAlchemy database URI to use SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///villain.db"
db = SQLAlchemy(app)

# Defining the Villain model
class Villain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    interests = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<Villain "+ self.name + ">"

with app.app_context():
	db.create_all()
	db.session.commit()

# ------------------------------
# Routes for serving Static HTML Files
# ------------------------------

@app.route("/")
def villain_cards():
  # Serves the main HTML page for viewing villains
  return app.send_static_file("villain.html")

@app.route("/add")
def add():
  # Serves the HTML form to add a villain
  return app.send_static_file("addvillain.html")

@app.route("/delete")
def delete():
  # Serves the HTML form to delete a villain
  return app.send_static_file("deletevillain.html")

# -----------------------------
# API Routes
# -----------------------------

@app.route("/api/villains/", methods=["GET"])
def get_villains():
   """Returns a list of all villains in the databse."""
   villains=Villain.query.all()
   data = []
   for villain in villains:
      data.append({
         "name" : villain.name,
         "description" : villain.description,
         "interests" : villain.interests,
         "url" : villain.url,
         "date_added" : villain.date_added
      })
   return jsonify(data)

@app.route("/api/villains/add", methods=["POST"])
def add_villain():
  """Adds a new villain to the database after validating input."""
  errors = []
  name = request.form.get("name")

# Validate inputs
  if not name:
    errors.append("Oops! Looks like you forgot a name!")

  description = request.form.get("description")
  if not description:
    errors.append("Oops! Looks like you forgot a description!")
  
  interests = request.form.get("interests")
  if not interests:
    errors.append("Oops! Looks like you forgot some interests!")
  
  url = request.form.get("url")
  if not url:
    errors.append("Oops! Looks like you forgot an image!")
  
  # Check if the villain name already exists
  villain = Villain.query.filter_by(name=name).first()
  if villain:
    errors.append("Oops! A villain with that name already exists!")
  
  if errors:
    return jsonify({"errors": errors})
  else:
    #Create and commit the new villain
    new_villain = Villain(name=name,description=description, interests=interests, url=url)
    db.session.add(new_villain)
    db.session.commit()
    return jsonify({"status":"success"})

@app.route("/api/villains/delete", methods=["POST"])
def delete_villain():
  name = request.form.get("name", "")
  villain = Villain.query.filter_by(name=name).first()
  if villain:
    db.session.delete(villain)
    db.session.commit()
    return jsonify({"status":"success"})
  else:
    return jsonify({"errors": ["Oops! A villain with that name doesn't exist!"]})

@app.route("/api/", methods=["GET"])
def get_endpoints():
   endpoints = {
      "/api/villains": "GET - Retrieves all villain data from the database",
      "/api/villains/delete": "POST - Deletes indicated villain if villain is in database",
      "/api/villains/add": "POST - Adds a villain to the database"
   }
   return jsonify(endpoints)

#-------------------------
# Run the flask server
#-------------------------
if __name__ == "__main__":
    app.run()