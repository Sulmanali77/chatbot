from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "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"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant named Salman GPT."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        reply = data["choices"][0]["message"]["content"]
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
