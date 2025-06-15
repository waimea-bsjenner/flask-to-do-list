#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html
import os
from app.helpers.session import init_session
from app.helpers.db import connect_db
from app.helpers.errors import register_error_handlers, not_found_error
from dotenv import load_dotenv

load_dotenv()
TURSO_URL = os.getenv("TURSO_URL")
TURSO_KEY = os.getenv("TURSO_KEY")

# Create the app
app = Flask(__name__)

# Setup a session for messages, etc.
init_session(app)

# Handle 404 and 500 errors
register_error_handlers(app)


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# tasks page route - Show all the tasks, and new task form
#-----------------------------------------------------------
@app.get("/")
def show_all_tasks():
    with connect_db() as client:
        # Get all the tasks from the DB
        sql = "SELECT * FROM tasks ORDER BY priority DESC"
        result = client.execute(sql)
        tasks = result.rows

        # And show them on the page
        return render_template("pages/tasks.jinja", tasks=tasks)


#-----------------------------------------------------------
# task page route - Show details of a single task
#-----------------------------------------------------------
@app.get("/task/<int:id>")
def show_one_task(id):
    with connect_db() as client:
        # Get the task details from the DB
        sql = "SELECT * FROM tasks WHERE id=?"
        values = [id]
        result = client.execute(sql, values)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            task = result.rows[0]
            return render_template("pages/task.jinja", task=task)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a task, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_task():
    # Get the data from the form
    name  = request.form.get("name")
    priority = request.form.get("priority")
    description = request.form.get("description")

    # Sanitise the inputs
    name = html.escape(name)
    priority = html.escape(priority)
    description = html.escape(description)
    with connect_db() as client:

        # Add the task to the DB
        sql = "INSERT INTO tasks (name, priority, description) VALUES (?, ?, ?)"
        values = [name, priority, description]
        client.execute(sql, values)

        # Go back to the home page
        flash(f"task '{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for completing a task
#-----------------------------------------------------------
@app.get("/complete/<int:id>")
def complete(id):
    with connect_db() as client:
        sql = "UPDATE complete FROM tasks WHERE id=?"
#-----------------------------------------------------------
# Route for deleting a task, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_task(id):
    with connect_db() as client:
        # Delete the task from the DB
        sql = "DELETE FROM tasks WHERE id=?"
        values = [id]
        client.execute(sql, values)

        # Go back to the home page
        flash("task deleted", "warning")
        return redirect("/")


