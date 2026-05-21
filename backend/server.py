from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import run_agent

app = Flask(__name__)
CORS(app) # Allows Next.js to securely talk to this Python server

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "No command provided"}), 400
    
    # Send the command to the ReAct loop in agent.py
    print(f"[*] Incoming command: {prompt}")
    response = run_agent(prompt)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    print("[*] Alpha Backend API is online on port 5000")
    app.run(port=5000)