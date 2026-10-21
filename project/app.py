from cs50 import SQL
from flask import Flask, redirect, render_template, jsonify, url_for, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from collections import defaultdict
import itertools

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///familyforest.db")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/add-person", methods=["GET", "POST"])
@login_required
def add_person():
    if request.method == "POST":
        if (
            not request.form.get("name")
            and not request.form.get("birthdate")
            and not request.form.get("notes")
        ):
            return render_template("add_person.html", error="At minimum of one information is required")

        name = request.form.get("name")
        if not name:
            name = "Unkown"

        birthdate = request.form.get("birthdate")
        if not birthdate:
            birthdate = "xxxx-xx-xx"

        notes = request.form.get("notes")
        if not notes:
            notes = ""

        db.execute(
            "INSERT INTO people (user_id, name, birth_date, notes) VALUES (?, ?, ?, ?)",
            session["user_id"], name, birthdate, notes
        )

        return redirect("/")

    return render_template("add_person.html")

@app.route("/add-relationship", methods=["GET", "POST"])
@login_required
def add_relationship():
    people = db.execute(
        "SELECT * FROM people WHERE user_id = ?",
        session["user_id"]
    )

    relationships = [
        "spouse",
        "parent",
        "sibling",
        "friend",
        "ex-spouse",
        "pet"
    ]

    if request.method == "POST":
        if not request.form.get("relationship"):
            return render_template(
                "add_relationship.html",
                people=people,
                relationships=relationships,
                error="Missing relationship"
            )

        if not request.form.get("personA"):
            return render_template(
                "add_relationship.html",
                people=people,
                relationships=relationships,
                error="Missing person A"
            )

        if not request.form.get("personB"):
            return render_template(
                "add_relationship.html",
                people=people,
                relationships=relationships,
                error="Missing person B"
            )

        if request.form.get("personA") == request.form.get("personB"):
            return render_template(
                "add_relationship.html",
                people=people,
                relationships=relationships,
                error="Person A and B should be different."
            )

        db.execute(
            "INSERT INTO relationships (user_id, person_a_id, person_b_id, relationship_type) VALUES (?, ?, ?, ?)",
            session["user_id"], request.form.get("personA"), request.form.get("personB"), request.form.get("relationship")
        )

        return redirect("/")

    return render_template("add_relationship.html", people=people, relationships=relationships)


@app.route("/person/<int:person_id>", methods=["GET", "POST"])
@login_required
def person(person_id):
    if request.method == "POST":
        return redirect(url_for("edit_person", person_id=person_id))

    person = db.execute(
        "SELECT * FROM people WHERE id = ? AND user_id = ?",
        person_id, session["user_id"]
    )[0]
    return render_template("person.html", person=person)


@app.route("/edit-person/", methods=["GET", "POST"])
@login_required
def edit_person():
    people = db.execute(
        "SELECT * FROM people WHERE user_id = ?",
        session["user_id"]
    )

    if request.method == "POST":
        if not request.form.get("person_id"):
            return render_template("edit_person.html", person=None, people=people, error="Missing person")
        return redirect(f"/edit-person/{request.form.get('person_id')}")

    return render_template("edit_person.html", person=None, people=people)


@app.route("/edit-person/<int:person_id>", methods=["GET", "POST"])
@login_required
def edit_person_id(person_id):
    if request.method == "POST":
        # Delete person
        if request.form.get("action") == "delete":
            db.execute(
                "DELETE FROM relationships WHERE (person_a_id = ? OR person_b_id = ?) AND user_id = ?",
                person_id, person_id, session["user_id"]
            )
            db.execute(
                "DELETE FROM people WHERE id = ? AND user_id = ?",
                person_id, session["user_id"]
            )

            return redirect("/")

        # Edit person

        # Save edited name
        name = request.form.get("name")
        if not request.form.get("name"):
            name = "Unkown"
        db.execute(
            "UPDATE people SET name = ? WHERE id = ? AND user_id = ?",
            request.form.get("name"), person_id, session["user_id"]
        )

        # Save edited birth date
        if request.form.get("birthdate"):
            db.execute(
                "UPDATE people SET birth_date = ? WHERE id = ? AND user_id = ?",
                request.form.get("birthdate"), person_id, session["user_id"]
            )

        # Save edited notes
        if request.form.get("notes"):
            db.execute(
                "UPDATE people SET notes = ? WHERE id = ? AND user_id = ?",
                request.form.get("notes"), person_id, session["user_id"]
            )

        return redirect(f"/")

    # Select person's info from database
    person = db.execute(
        "SELECT * FROM people WHERE id = ? AND user_id = ?",
        person_id, session["user_id"]
    )[0]
    return render_template("edit_person.html", person=person)


@app.route("/edit-relationship/", methods=["GET", "POST"])
@login_required
def edit_relationship():
    relationships = db.execute(
        """
        SELECT r.id,
               r.relationship_type,
               pa.name AS person_a_name,
               pb.name AS person_b_name
        FROM relationships r
        JOIN people pa ON pa.id = r.person_a_id
        JOIN people pb ON pb.id = r.person_b_id
        WHERE r.user_id = ?
        """,
        session["user_id"]
    )

    if request.method == "POST":
        relationship_id = request.form.get("relationship_id")

        if not relationship_id:
            return render_template(
                "edit_relationship.html",
                relationship=None,
                relationships=relationships,
                error="Missing relationship"
            )

        return redirect(f"/edit-relationship/{relationship_id}")

    return render_template(
        "edit_relationship.html",
        relationship=None,
        relationships=relationships
    )

@app.route("/edit-relationship/<int:relationship_id>", methods=["GET", "POST"])
@login_required
def edit_relationship_id(relationship_id):

    if request.method == "POST":
        action = request.form.get("action")

        # DELETE
        if action == "delete":
            db.execute(
                "DELETE FROM relationships WHERE id = ? AND user_id = ?",
                relationship_id,
                session["user_id"]
            )
            return redirect("/")

        # SAVE EDITS
        db.execute(
            """
            UPDATE relationships
            SET relationship_type = ?
            WHERE id = ? AND user_id = ?
            """,
            request.form.get("relationship_type"),
            relationship_id,
            session["user_id"]
        )

        return redirect("/")

    # GET relationship info
    relationship = db.execute(
        """
        SELECT r.id,
               r.relationship_type,
               pa.name AS person_a_name,
               pb.name AS person_b_name
        FROM relationships r
        JOIN people pa ON pa.id = r.person_a_id
        JOIN people pb ON pb.id = r.person_b_id
        WHERE r.id = ? AND r.user_id = ?
        """,
        relationship_id,
        session["user_id"]
    )

    if not relationship:
        return redirect("/edit-relationship/")

    return render_template(
        "edit_relationship.html",
        relationship=relationship[0]
    )



@app.route("/login", methods=["GET", "POST"])
def login():
    # Erase previous session data
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error="Username missing")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="Password missing")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            # Redirects to register if user does not exist
            if len(rows) == 0:
                return redirect("/register")

            return render_template("login.html", error="Incorrect username or password")

        # Saves user data
        session["user_id"] = rows[0]["id"]
        session["username"] = request.form.get("username")

        # Redirects to homepage
        return redirect("/")

    # User reached route via GET
    return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget user data
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Erase previous session data
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", error="Username missing")

        # Ensure name was submitter
        if not request.form.get("username"):
            return render_template("register.html", error="Name missing")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("register.html", error="Password missing")

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return render_template("register.html", error="Confirmation missing")

        # Ensure password and confirmation are identical
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", error="Password and confirmation must be identical")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Redirect to login if user in database
        if len(rows) != 0:
            return redirect("/login")

        # Save new user in database
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            request.form.get("username"), generate_password_hash(request.form.get("password"))
        )

        # Remember data in session
        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE username = ?",
            request.form.get("username")
        )[0]["id"]
        session["username"] = request.form.get("username")

        # Add first person to the database
        db.execute(
            "INSERT INTO people (user_id, name) VALUES(?, ?)",
            session["user_id"], request.form.get("name")
        )

        return redirect("/")

    # User reached route via GET
    return render_template("register.html")


@app.route("/graph-data")
@login_required
def graph_data():

    # -----------------------------
    # Nodes
    # -----------------------------
    people = db.execute(
        "SELECT id, name FROM people WHERE user_id = ?",
        session["user_id"]
    )

    nodes = [
        {
            "id": p["id"],
            "label": p["name"],
            "group": "person"
        }
        for p in people
    ]

    # -----------------------------
    # Base relationships
    # -----------------------------
    relationships = db.execute(
        """
        SELECT person_a_id, person_b_id, relationship_type
        FROM relationships
        WHERE user_id = ?
        """,
        session["user_id"]
    )

    edges = [
        {
            "from": r["person_a_id"],
            "to": r["person_b_id"],
            "type": r["relationship_type"]
        }
        for r in relationships
    ]

    # -----------------------------
    # Build siblings dynamically
    # -----------------------------
    parents = db.execute(
        """
        SELECT person_a_id, person_b_id
        FROM relationships
        WHERE user_id = ?
          AND relationship_type = 'parent'
        """,
        session["user_id"]
    )

    # Group children by parent
    children_by_parent = defaultdict(list)
    for row in parents:
        children_by_parent[row["person_a_id"]].append(row["person_b_id"])

    # Track existing edges to avoid duplicates
    existing = {
        (
            min(e["from"], e["to"]),
            max(e["from"], e["to"]),
            e["type"]
        )
        for e in edges
    }

    # Create sibling edges
    for children in children_by_parent.values():
        if len(children) < 2:
            continue

        for a, b in itertools.combinations(children, 2):
            key = (min(a, b), max(a, b), "sibling")

            if key not in existing:
                edges.append({
                    "from": a,
                    "to": b,
                    "type": "sibling"
                })
                existing.add(key)

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })
