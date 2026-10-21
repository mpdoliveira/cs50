import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    portfolio = []

    # Locate all user's transactions
    transactions = db.execute(
        "SELECT * FROM stock_transactions WHERE username = ?", session["username"])

    # Compute transations
    for transaction in transactions:
        found = False
        for stock in portfolio:
            if stock["symbol"] == transaction["symbol"]:
                stock["shares"] += transaction["shares"]
                found = True
                break
        if not found:
            stock = lookup(transaction["symbol"])
            stock["shares"] = transaction["shares"]
            portfolio.append(stock)

    # Compute total in USD
    total = 0
    for stock in portfolio:
        stock["total"] = stock["shares"] * stock["price"]
        total += stock["total"]
        stock["total"] = usd(stock["total"])
        stock["price"] = usd(stock["price"])
    total = usd(total)

    cash = usd(db.execute(
        "SELECT cash FROM users WHERE username = ?",
        session["username"]
    )[0]["cash"])

    return render_template("index.html", cash=cash, portfolio=portfolio, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        # Ensure symbol exists
        if not request.form.get("symbol"):
            return apology("must provide stock symbol", 400)

        # Ensure shares exists
        shares = request.form.get("shares")
        if not shares:
            return apology("must provide number of shares", 400)

        if not shares.isnumeric() or int(shares) < 0:
            return apology("must provide valid number of shares", 400)
        shares = int(shares)

        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("could not find coresponding stock")

        user = db.execute("SELECT * FROM users WHERE username = ?", session["username"])[0]
        total = stock["price"] * shares

        # Ensure user has enough money
        if total > user["cash"]:
            return apology("insuficient cash")

        # Subtract total from user's cash
        db.execute(
            "UPDATE users SET cash = cash - ? WHERE username = ?",
            total, session["username"]
        )

        # Log transaction (+)
        db.execute(
            "INSERT INTO stock_transactions (username, shares, symbol, price, date, time) VALUES(?, ?, ?, ?, ?, ?)",
            session["username"], shares, stock["symbol"], total, date.today(), datetime.now().time()
        )

        return redirect("/")
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT * FROM stock_transactions WHERE username = ?",
        session["username"]
    )
    for transaction in transactions:
        transaction["price"] = usd(transaction["price"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = request.form.get("username")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if "quoted" not in session:
        session["quoted"] = []

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide stock symbol", 400)
        lookup_result = lookup(request.form.get("symbol"))
        if not lookup_result:
            return apology("could not find coresponding stock")
        prev = False
        for quote in session["quoted"]:
            if quote["symbol"] == lookup_result["symbol"]:
                quote["price"] = usd(lookup_result["price"])
                prev = True
        if not prev:
            lookup_result["price"] = usd(lookup_result["price"])
            session["quoted"].append(lookup_result)
    return render_template("quote.html", quoted=session["quoted"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return redirect("login.html", 400)

        password = request.form.get("password", 400)
        if not password:
            return apology("must provide password", 400)

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide confirmation", 400)
        if password != confirmation:
            return apology("password and confirmation must be identical", 400)
        
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            username, generate_password_hash(password)
        )

        session["user_id"] = int(db.execute(
            "SELECT id FROM users WHERE username = ?",
            username
        )[0]["id"])
        session["username"] = username
        return redirect("/")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Ensure symbol exists
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide stock symbol", 400)

        # Ensure number of shares exist
        shares = int(request.form.get("shares"))
        if not shares:
            return apology("must provide number of shares", 400)

        # Ensure symbol coresponds to existind stock
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("could not find coresponding stock")

        # Get number of stock shares the user has
        transactions = db.execute(
            "SELECT shares FROM stock_transactions WHERE username = ? AND symbol = ?",
            session["username"], symbol
        )
        user_shares = 0
        for transaction in transactions:
            user_shares += transaction["shares"]

        # Ensure user has suficient shares to sell
        if user_shares < shares:
            return apology("You have insuficient shares")

        # Add total to user's cash
        total = stock["price"] * shares
        db.execute(
            "UPDATE users SET cash = cash + ? WHERE username = ?",
            total, session["username"]
        )

        # Log transaction (-)
        db.execute(
            "INSERT INTO stock_transactions (username, shares, symbol, price, date, time) VALUES(?, ?, ?, ?, ?, ?)",
            session["username"], -shares, stock["symbol"], total, date.today(), datetime.now().time()
        )
        return redirect("/")

    # Locate all user's transactions
    transactions = db.execute(
        "SELECT * FROM stock_transactions WHERE username = ?", session["username"])

    portfolio = []
    # Compute transations
    for transaction in transactions:
        found = False
        for stock in portfolio:
            if stock["symbol"] == transaction["symbol"]:
                stock["shares"] += transaction["shares"]
                found = True
                break
        if not found:
            stock = lookup(transaction["symbol"])
            stock["shares"] = transaction["shares"]
            portfolio.append(stock)

    return render_template("sell.html", portfolio=portfolio)


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    """Manage cash."""

    user_cash = db.execute(
        "SELECT cash FROM users WHERE username = ?", session["username"]
    )[0]
    user_cash = user_cash["cash"]

    if request.method == "POST":
        # Ensure value exists
        if not request.form.get("value"):
            return apology("must provide value", 400)

        # Ensure type of transaction exists
        if not request.form.get("type"):
            return apoloy("must provide type of transaction", 400)

        if request.form.get("type") == "deposit":
            user_cash += float(request.form.get("value"))
            db.execute(
                "UPDATE users SET cash = ? WHERE username = ?",
                user_cash, session["username"]
            )
        elif request.form.get("type") == "withdraw":
            if float(request.form.get("value")) > user_cash:
                return apology("Insuficient cahs")
            user_cash -= float(request.form.get("value"))
            db.execute(
                "UPDATE users SET cash = ? WHERE username = ?",
                user_cash, session["username"]
            )
    return render_template("cash.html", cash=usd(user_cash))
