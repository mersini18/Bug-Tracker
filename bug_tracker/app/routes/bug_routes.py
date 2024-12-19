from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Bug, Project, User


bug_bp = Blueprint('bug', __name__, url_prefix='/home')

@bug_bp.route('/', methods=['GET'])
@login_required
def home():
    bugs = Bug.query.all()

    return render_template('home.html', username=current_user.username, bugs=bugs, show_navbar=True)

@bug_bp.route('/add-bug', methods=['GET', 'POST'])
@login_required
def add_bug():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        status = request.form.get('status')
        assigned_to = request.form.get('assigned_to')
        project_id = request.form.get('project_id')

        if not title:
            flash('Bug title is required', 'error')
            return redirect(url_for('bug.add_bug'))
        if not description:
            flash('Bug description is required', 'error')
            return redirect(url_for('bug.add_bug'))
        if not project_id:
            flash('Bug project id is required', 'error')
            return redirect(url_for('bug.add_bug'))
        
        new_bug = Bug(
            title = title,
            description = description,
            priority = priority,
            status = status,
            project_id = project_id,
            reported_by = current_user.username,
            assigned_to = assigned_to if assigned_to else None
        )

        db.session.add(new_bug)
        db.session.commit()

        flash('Bug created successfully', 'success')
        return redirect(url_for('bug.home'))
    
    projects = Project.query.all()
    users = User.query.all()
    return render_template('add_bug.html', projects=projects, users=users)

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