from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Load your OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/parse-task", methods=["POST"])
def parse_task():
    # Check if API key is set
    if not openai.api_key:
        return jsonify({"error": "Missing OpenAI API key"}), 500

    data = request.get_json()
    task_text = data.get("task_text", "")

    if not task_text:
        return jsonify({"error": "Missing task_text"}), 400

    prompt = f"""
You are a task parser for Notion. Convert this natural language into a JSON object with:
- title
- responsibility
- project
- due_date (ISO format)
- description

Input: {task_text}
Output (JSON only):
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You convert text into structured task JSON."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.3,
            max_tokens=200)

        # Get and format the result
        json_output = response["choices"][0]["message"]["content"].strip()

        # Safe parsing using literal_eval instead of eval (safer!)
        import ast
        parsed_output = ast.literal_eval(json_output)

        return jsonify(parsed_output)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # IMPORTANT: Replit expects port 8080
