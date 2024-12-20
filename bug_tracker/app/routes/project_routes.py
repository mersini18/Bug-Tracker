from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Project, User

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
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
    
        if not name:
            flash('Project title is required', 'error')
            render_template('add_project.html')
        
        new_project = Project(
            name=name,
            description=description 
        )
        
        db.session.add(new_project)
        db.session.commit()

        flash('Project created successfully', 'success')
        return redirect(url_for('project.projects'))

    projects = Project.query.all
    return render_template('add_project.html', projects=projects)