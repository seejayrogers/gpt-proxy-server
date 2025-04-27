from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime

# 🆕 You must define 'app' first
app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route("/parse-task", methods=["POST"])
def parse_task():
    data = request.get_json()
    task_text = data.get("task_text", "")

    if not task_text:
        return jsonify({"error": "Missing task_text"}), 400

    # Inject today's date into the prompt
    today_date = datetime.utcnow().date().isoformat()

    prompt = f"""
Today is {today_date}.
You are a task parser for Notion. Convert this natural language into a JSON object with:
- title
- responsibility
- project
- due_date (ISO format, like 2025-04-27)
- description

Input:
{task_text}

Output (JSON only):
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You convert text into structured task JSON for Notion."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        json_output = response.choices[0].message.content.strip()
        return jsonify(eval(json_output))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
