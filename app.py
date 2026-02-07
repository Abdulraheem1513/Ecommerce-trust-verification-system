from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ecom_trust_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecom_trust.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route("/")
def home():
    return render_template("index.html", year=2026)


@app.route("/check", methods=["GET", "POST"])
def check():
    result = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        matched_reports = Report.query.filter(
            Report.seller.ilike(f"%{query}%")
        ).all()

        score = max(0, 100 - (len(matched_reports) * 25))

        if score >= 70:
            status = "Safe"
        elif score >= 40:
            status = "Caution"
        else:
            status = "High Risk"

        result = {
            "query": query,
            "score": score,
            "status": status,
            "matches": matched_reports
        }

    return render_template("check.html", result=result, year=2026)


@app.route("/report", methods=["GET", "POST"])
def report():
    message = None

    if request.method == "POST":
        seller = request.form.get("seller", "").strip()
        details = request.form.get("details", "").strip()

        if not seller or not details:
            message = "⚠️ Please fill in both Seller and Details."
        else:
            new_report = Report(seller=seller, details=details)
            db.session.add(new_report)
            db.session.commit()
            message = "✅ Report submitted successfully. Thank you!"

    return render_template("report.html", message=message, year=2026)

@app.route("/reports")
def reports_page():
    all_reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("reports.html", reports=all_reports, year=2026)

@app.route("/about")
def about():
    return render_template("about.html", year=2026)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   

    app.run(debug=True)
