from flask import Flask, request, jsonify, render_template
from datetime import datetime
import threading
from db import events

app = Flask(__name__)

def store_event(event_type, payload):
    if event_type == "push":
        author = payload["pusher"]["name"]
        to_branch = payload["ref"].split("/")[-1]
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        msg = f'{author} pushed to {to_branch} on {timestamp}'
    elif event_type == "pull_request":
        author = payload["sender"]["login"]
        from_branch = payload["pull_request"]["head"]["ref"]
        to_branch = payload["pull_request"]["base"]["ref"]
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        msg = f'{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}'
    elif event_type == "pull_request" and payload["action"] == "closed" and payload["pull_request"]["merged"]:
        author = payload["sender"]["login"]
        from_branch = payload["pull_request"]["head"]["ref"]
        to_branch = payload["pull_request"]["base"]["ref"]
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        msg = f'{author} merged branch {from_branch} to {to_branch} on {timestamp}'
    else:
        return

    events.insert_one({"message": msg, "timestamp": datetime.utcnow()})

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event")
    threading.Thread(target=store_event, args=(event_type, payload)).start()
    return '', 200

@app.route('/events', methods=['GET'])
def get_events():
    last_events = list(events.find().sort("timestamp", -1).limit(10))
    return jsonify([e["message"] for e in last_events])

if __name__ == '__main__':
    app.run(debug=True, port=5000)