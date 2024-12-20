from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Bug, Project, User
from app.forms import BugForm


bug_bp = Blueprint('bug', __name__, url_prefix='/home')

@bug_bp.route('/', methods=['GET'])
@login_required
def home():
    bugs = Bug.query.all()

    return render_template('home.html', username=current_user.username, bugs=bugs, show_navbar=True)

@bug_bp.route('/add-bug', methods=['GET', 'POST'])
@login_required
def add_bug():
    form = BugForm()

    form.project_id.choices = [(project.id, project.name) for project in Project.query.all()]
    form.assigned_to.choices = [(user.username, user.username) for user in User.query.all()]
    form.assigned_to.choices.insert(0, ("", "Unassigned")) 

    if form.validate_on_submit():
        new_bug = Bug(
            title = form.title.data,
            description = form.description.data,
            priority = form.priority.data,
            status = form.status.data,
            project_id = form.project_id.data,
            reported_by = current_user.username,
            assigned_to = form.assigned_to.data if form.assigned_to.data else None
        )

        db.session.add(new_bug)
        db.session.commit()

        flash('Bug created successfully', 'success')
        return redirect(url_for('bug.home'))
    
    projects = Project.query.all()
    users = User.query.all()
    return render_template('add_bug.html', form=form, projects=projects, users=users)

@bug_bp.route('/delete-bug/<int:bug_id>', methods=['POST'])
@login_required
def delete_bug(bug_id):
    # Ensure only admins can delete bugs
    if current_user.role != 'admin':
        flash("You do not have permission to delete bugs.", "error")
        return redirect(url_for('bug.home'))

    # Query for the bug
    bug = Bug.query.get_or_404(bug_id)

    # Delete the bug
    db.session.delete(bug)
    db.session.commit()

    flash("Bug deleted successfully.", "success")
    return redirect(url_for('bug.home'))