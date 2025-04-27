from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 🆕 Master Project List mapping (Project Name ➔ Design Manager)
project_design_manager = {
    "Redondo Beach": "Nick Zent",
    "InSite Development": "Andrew Urban",
    "San Diego Storage": "Javi Carrasco",
    "Manhattan Beach Expansion": "Hanneli Salenius-Lundberg",
    "Pasadena Build": "Utkarsh Kumar"
    # ➔ You can add more projects here as needed
}

@app.route("/parse-task", methods=["POST"])
def parse_task():
    data = request.get_json()
    task_text = data.get("task_text", "")

    if not task_text:
        return jsonify({"error": "Missing task_text"}), 400

    # 🗓️ Inject today's date into the prompt
    today_date = datetime.utcnow().date().isoformat()

    prompt = f"""
Today is {today_date}.
You are a task parser for Notion. Convert this natural language into a JSON object with:
- title
- responsibility (leave blank if unknown)
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
            max_tokens=300
        )

        # Parse the returned JSON from GPT
        json_output = response.choices[0].message.content.strip()
        task_data = eval(json_output)

        # 🆕 After parsing: Lookup and assign correct Design Manager
        project_name = task_data.get("project", "").strip()
        if project_name in project_design_manager:
            task_data["responsibility"] = project_design_manager[project_name]

        return jsonify(task_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
