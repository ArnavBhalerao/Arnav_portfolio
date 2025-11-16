from flask import Flask, request, render_template, redirect, url_for, flash
from pymongo import MongoClient
from datetime import datetime

# ---------------------------------------------------
# HARDCODED CONFIG (YOU ASKED FOR THIS)
# ---------------------------------------------------

MONGODB_URI = "mongodb+srv://arnavbhalerao:arnavbhalerao2208@cluster0.q7kigt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "portfolio"
SECRET_KEY = "supersecret123"

# ---------------------------------------------------
# FLASK + MONGO SETUP
# ---------------------------------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

contacts_col = db.contacts
about_col = db.about
skills_col = db.skills
projects_col = db.projects
education_col = db.education


# ---------------------------------------------------
# HOME ROUTE
# ---------------------------------------------------

@app.route("/")
def index():
    about = about_col.find_one() or {}
    skills = list(skills_col.find().sort("order", 1))
    projects = list(projects_col.find().sort("order", 1))
    education = list(education_col.find().sort("order", -1))

    return render_template(
        "index.html",
        about=about,
        skills=skills,
        projects=projects,
        education=education
    )


# ---------------------------------------------------
# CONTACT FORM (NO JS — plain HTML form submission)
# ---------------------------------------------------

@app.route("/contact", methods=["POST"])
def contact():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()

    if not (name and email and message):
        flash("Please fill all fields.", "error")
        return redirect(url_for("index") + "#contact")

    # save to mongodb
    contacts_col.insert_one({
        "name": name,
        "email": email,
        "message": message,
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent"),
        "created_at": datetime.utcnow()
    })

    return render_template("contact_sent.html", name=name)


# ---------------------------------------------------
# HEALTH CHECK (for Render)
# ---------------------------------------------------

@app.route("/_health")
def health():
    try:
        client.admin.command("ping")
        return {"ok": True}
    except:
        return {"ok": False}, 500


# ---------------------------------------------------
# RUN
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
