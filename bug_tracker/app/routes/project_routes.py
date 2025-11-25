from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Project, User
from app.forms import ProjectForm

projects_bp = Blueprint('project', __name__, url_prefix='/projects')

@projects_bp.route('/projects', methods=['GET'])
@login_required
def projects():
    projects = Project.query.all()

    return render_template('projects.html', projects=projects)

@projects_bp.route('/delete-project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    if current_user.role != 'admin':
        flash("You do not have permission to delete projects.", "error")
        return redirect(url_for('project.projects'))
    
    project = Project.query.get_or_404(project_id)

    db.session.delete(project)
    db.session.commit()

    flash("Project deleted successfully.", "success")
    return redirect(url_for('project.projects'))


@projects_bp.route('/add-project', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()

    if form.validate_on_submit():
        new_project = Project(
            name = form.name.data,
            description = form.description.data
        )

        db.session.add(new_project)
        db.session.commit()

        flash('Project created successfully', 'success')
        return redirect(url_for('project.projects'))
    
    projects = Project.query.all()

    return render_template('add_project.html', form=form, projects=projects)