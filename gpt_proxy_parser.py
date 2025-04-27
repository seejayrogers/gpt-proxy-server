@app.route("/parse-task", methods=["POST"])
def parse_task():
    data = request.get_json()
    task_text = data.get("task_text", "")

    if not task_text:
        return jsonify({"error": "Missing task_text"}), 400

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
                {"role": "system", "content": "You convert task descriptions into structured JSON for Notion."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        json_output = response.choices[0].message.content.strip()
        task_data = eval(json_output)

        # --- Responsibility Lookup ---
        project_name = task_data.get("project", "").strip()
        if project_name in project_design_manager:
            assigned_manager = project_design_manager[project_name]
            if assigned_manager:
                task_data["responsibility"] = assigned_manager
            else:
                task_data["responsibility"] = "Samantha Moffitt"
                task_data["description"] += " (⚠️ No Design Manager assigned — Samantha assigned by default.)"
        else:
            task_data["responsibility"] = "Samantha Moffitt"
            task_data["description"] += " (⚠️ Project not recognized — Samantha assigned by default.)"

        # --- Priority Calculation ---
        due_date_str = task_data.get("due_date")
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
                days_until_due = (due_date - datetime.utcnow()).days
                if days_until_due <= 3:
                    task_data["priority"] = "High"
                else:
                    task_data["priority"] = "Normal"
            except Exception as e:
                task_data["priority"] = "Normal"
        else:
            task_data["priority"] = "Normal"

        return jsonify(task_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
