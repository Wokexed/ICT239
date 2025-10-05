from flask import Flask, render_template, request, redirect, url_for
from app import app
from app.form import TaskForm
from app.model import Task

tasks = [
    {
        "task_id": 1,
        "title": "Finish project report",
        "description": "Complete the final draft of the inventory management project report.",
        "start_date": "2025-10-02",
        "due_date": "2025-10-05",
        "priority": "High"
    },
    {
        "task_id": 2,
        "title": "Grocery shopping",
        "description": "Buy weekly groceries: milk, eggs, bread, and vegetables.",
        "start_date": "2025-10-01",
        "due_date": "2025-10-01",
        "priority": "Medium"
    },
    {
        "task_id": 3,
        "title": "Gym workout",
        "description": "Leg day workout at the gym. Focus on squats and lunges.",
        "start_date": "2025-10-01",
        "due_date": "2025-10-01",
        "priority": "Low"
    },
    {
        "task_id": 4,
        "title": "Doctor appointment",
        "description": "Visit Dr. Tan for follow-up consultation on allergy treatment.",
        "start_date": "2025-10-03",
        "due_date": "2025-10-03",
        "priority": "High"
    },
    {
        "task_id": 5,
        "title": "Team meeting",
        "description": "Weekly sync-up with the development team to review progress.",
        "start_date": "2025-10-04",
        "due_date": "2025-10-04",
        "priority": "Medium"
    }

]

@app.route('/')
def hello_world():
    # for task in tasks:
    #     Task.add_task(task)
    tasks = Task.get_all_tasks()

    return render_template("todo.html", tasks=tasks)

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    # render a new form
    form = TaskForm()
    if request.method == "GET":
        return render_template("edit.html", form=form, task_id=task_id)
    if request.method == "POST":
        if form.validate_on_submit():
            Task.update_task(task_id, {
                "title": form.title.data,
                "description": form.description.data,
                "start_date": form.start_date.data.strftime('%Y-%m-%d'),
                "due_date": form.due_date.data.strftime('%Y-%m-%d'),
                "priority": form.priority.data,
                "task_id": task_id
            })

            return redirect(url_for('hello_world'))

    # reterive task by id
    # modifty the task based on form data
    return f"Edit task with ID: {task_id} - Feature under construction"

@app.route("/add", methods=["GET", "POST"])
def add_task():
    form = TaskForm()
    if request.method == "GET":
        return render_template("add.html", form=form)
    if request.method == "POST":
        if form.validate_on_submit():
            tasks = Task.get_all_tasks()
            new_task = {
                "task_id": max(task["task_id"] for task in tasks) + 1 if tasks else 1,
                "title": form.title.data,
                "description": form.description.data,
                "start_date": form.start_date.data.strftime('%Y-%m-%d'),
                "due_date": form.due_date.data.strftime('%Y-%m-%d'),
                "priority": form.priority.data
            }
            Task.add_task(new_task)
            return redirect(url_for('hello_world'))
        return render_template("add.html", form=form)

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    for id, task in enumerate(tasks):
        if task["task_id"] == task_id:
            tasks.pop(id)
            break

    return render_template("todo.html", tasks=tasks)

