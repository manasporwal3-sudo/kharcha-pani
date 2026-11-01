import os
import json
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK (Vercel + local).
if not firebase_admin._apps:
    try:
        if os.environ.get("FIREBASE_CREDENTIALS"):
            try:
                raw_cred = os.environ.get("FIREBASE_CREDENTIALS")
                # Fix for escaped newlines in Vercel environment variables
                raw_cred = raw_cred.replace('\\n', '\n')
                cred_dict = json.loads(raw_cred)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid FIREBASE_CREDENTIALS JSON: {e}")
            cred = credentials.Certificate(cred_dict)
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        elif os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
        else:
            raise RuntimeError(
                "No Firebase credentials found. Set FIREBASE_CREDENTIALS env var "
                "(JSON string) or GOOGLE_APPLICATION_CREDENTIALS / serviceAccountKey.json."
            )
        firebase_admin.initialize_app(cred)
    except Exception as e:
        raise RuntimeError(f"Firebase initialization failed: {e}") from e

db = firestore.client()
expenses_collection = db.collection("expenses")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    docs = expenses_collection.order_by(
        "timestamp", direction=firestore.Query.DESCENDING
    ).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        result.append(data)
    return jsonify(result)


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    category = (payload.get("category") or "").strip()
    amount_raw = payload.get("amount")

    if not title:
        return jsonify({"error": "title is required"}), 400
    if not category:
        return jsonify({"error": "category is required"}), 400
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400
    if amount <= 0:
        return jsonify({"error": "amount must be greater than 0"}), 400

    doc = {
        "title": title,
        "amount": amount,
        "category": category,
        "timestamp": datetime.now(timezone.utc),
    }
    ref = expenses_collection.add(doc)
    doc["id"] = ref[1].id
    doc["timestamp"] = doc["timestamp"].isoformat()
    return jsonify(doc), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
