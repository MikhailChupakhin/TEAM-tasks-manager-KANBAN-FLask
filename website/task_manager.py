from flask import Blueprint, render_template, jsonify, request, abort
from flask import session, redirect, url_for
from . import db
from website.forms import ProjectCreationForm, TaskCreationForm, InviteCreationForm, RemoveMemberForm, TaskEditForm
from website.models import Project, Invitation, User, Task, TaskComment
from .breadcrumbs import breadcrumbs_tmv, breadcrumbs_op
from .filters import status_abbreviate
task_manager_bp = Blueprint('task_manager', __name__)


def is_authenticated():
    return 'user_id' in session


def login_required(view):
    def wrapped(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


@task_manager_bp.route('/', endpoint='task_manager', methods=['GET', 'POST'])
@login_required
def task_manager_view():
    breadcrumbs = breadcrumbs_tmv
    current_user = User.query.get(session['user_id'])
    csrf_token = session.get('csrf_token', '')
    project_form = ProjectCreationForm()


    # Получаем собств. проекты и проекты с подтв. инвайтами
    user_projects = Project.query.filter_by(owner=current_user.id).all()
    accepted_invitations = Invitation.query.filter_by(received_by_id=current_user.id, is_accepted=True).all()
    all_projects = user_projects + [invitation.project for invitation in accepted_invitations]

    all_projects.sort(key=lambda project: project.created_at, reverse=True)
    for project in all_projects:
        project.calculate_tasks_count()

    pending_invitations = Invitation.query.filter_by(received_by_id=current_user.id, is_accepted=False).all()
    pending_invitations_count = len(pending_invitations)

    if project_form.validate_on_submit():
        name = project_form.name.data
        description = project_form.description.data
        type = project_form.type.data
        owner = current_user.id

        project = Project(name=name, description=description, owner=owner, type=type)
        project.add_event_to_log("Проект создан", current_user) ## Журналирование
        db.session.add(project)
        db.session.commit()

        return redirect(url_for('task_manager.task_manager'))

    return render_template('task_manager.html',
                           breadcrumbs=breadcrumbs,
                           all_projects=all_projects,
                           project_form=project_form,
                           current_user=current_user.id,
                           csrf_token=csrf_token,
                           pending_invitations=pending_invitations,
                           pending_invitations_count=pending_invitations_count)

### РОУТЫ ПРОЕКТОВ(создание проектов - в POST task_manager_view)


@task_manager_bp.route('/delete_project/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)
    current_user = User.query.get(session['user_id'])
    if project:
        if project.owner == current_user.id:
            db.session.delete(project)
            db.session.commit()
            return jsonify({'message': 'Проект успешно удален.'}), 200
        else:
            return jsonify({'message': 'У вас нет прав для удаления этого проекта.'}), 403
    else:
        return jsonify({'message': 'Проект не найден.'}), 404


@task_manager_bp.route('/project/basic/<int:project_id>', endpoint='basic_project')
@login_required
def open_basic_project(project_id):
    breadcrumbs = breadcrumbs_op
    project = Project.query.get(project_id)
    task_form = TaskCreationForm()
    task_edit_form = TaskEditForm()
    tm_invite_form = InviteCreationForm()
    tm_remove_form = RemoveMemberForm()

    if project is None:
        return "Проект не найден", 404

    current_user_id = session.get('user_id')
    members_ids = project.get_active_members_ids()
    if current_user_id in members_ids:
        tasks = sorted(Task.query.filter_by(project_id=project_id).all(), key=lambda task: task.deadline)
        owner = User.query.get(project.owner)

        task_form.responsible.choices = project.get_members_choices()
        task_edit_form.responsible.choices = project.get_members_choices()
        project_members = project.members_roles

        return render_template('basic_project.html',
                               breadcrumbs=breadcrumbs,
                               project=project,
                               task_form=task_form,
                               task_edit_form=task_edit_form,
                               tm_invite_form=tm_invite_form,
                               tm_remove_form=tm_remove_form,
                               tasks=tasks,
                               project_members=project_members,
                               owner=owner,
                               is_owner=True
                               )
    else:
        return "Требуется приглашение, чтобы просматривать этот проект."


@task_manager_bp.route('/project/devflow/<int:project_id>', endpoint='devflow_project')
@login_required
def open_devflow_project(project_id):
    breadcrumbs = breadcrumbs_op
    project = Project.query.get(project_id)
    task_form = TaskCreationForm()
    task_edit_form = TaskEditForm()
    tm_invite_form = InviteCreationForm()
    tm_remove_form = RemoveMemberForm()

    if project is None:
        return "Проект не найден", 404

    current_user_id = session.get('user_id')
    members_ids = project.get_active_members_ids()
    if current_user_id in members_ids:
        tasks = sorted(Task.query.filter_by(project_id=project_id).all(), key=lambda task: task.deadline)
        owner = User.query.get(project.owner)

        task_form.responsible.choices = project.get_members_choices()
        task_edit_form.responsible.choices = project.get_members_choices()
        project_members = project.members_roles

        return render_template('devflow_project.html',
                               breadcrumbs=breadcrumbs,
                               project=project,
                               task_form=task_form,
                               task_edit_form=task_edit_form,
                               tm_invite_form=tm_invite_form,
                               tm_remove_form=tm_remove_form,
                               tasks=tasks,
                               project_members=project_members,
                               owner=owner,
                               is_owner=True
                               )
    else:
        return "Требуется приглашение, чтобы просматривать этот проект."


@task_manager_bp.route('/project/<int:project_id>/log', methods=['GET'], endpoint='log')
@login_required
def view_project_log(project_id):
    project = Project.query.get(project_id)

    if project is None:
        abort(404)

    event_log_lines = project.event_log.split('\n') if project.event_log else []
    event_log_lines.pop()

    return render_template('project_log.html', project=project, event_log=event_log_lines)


### РОУТЫ ЗАДАЧ


@task_manager_bp.route('/project/<string:project_type>/<int:project_id>/create_task', methods=['POST'], endpoint='create_task')
@login_required
def create_task(project_type, project_id):
    project = Project.query.get(project_id)
    task_form = TaskCreationForm()

    task_form.responsible.choices = project.get_members_choices()

    if task_form.validate_on_submit():
        name = task_form.name.data
        description = task_form.description.data
        deadline = task_form.deadline.data
        responsible_id = task_form.responsible.data
        responsible_user = User.query.get(responsible_id)

        # Создание объекта задачи
        task = Task(name=name, description=description, project_id=project_id, deadline=deadline, responsible=responsible_user)

        db.session.add(task)
        current_user = User.query.get(session.get('user_id'))
        project.add_event_to_log(f'Добавлена задача: "{task.name}"', current_user)  ## Журналирование
        db.session.commit()

        if project_type == 'basic':
            return redirect(url_for('task_manager.basic_project', project_id=project_id))
        elif project_type == 'devflow':
            return redirect(url_for('task_manager.devflow_project', project_id=project_id))

    for field, errors in task_form.errors.items():
        for error in errors:
            print(f"Ошибка в поле '{getattr(task_form, field).label.text}': {error}", 'error')
    return 'Что-то пошло не так'


@task_manager_bp.route('/project/<int:project_id>/edit_task_modal/<int:task_id>', methods=['POST'], endpoint='edit_task')
@login_required
def edit_task_modal(project_id, task_id):
    data = request.json
    project = Project.query.get(project_id)
    task = Task.query.get(task_id)

    if task is None or task.project_id != project_id:
        return "Задача не найдена", 404

    task.name = data.get('task-name')
    task.description = data.get('task-description')
    task.deadline = data.get('task-deadline')

    # Получаем ID ответственного из JSON и соотв. пользователя
    task_responsible = request.json['task-responsible']
    responsible = User.query.get(int(task_responsible))

    if responsible is not None:
        task.responsible = responsible

    current_user = User.query.get(session['user_id'])
    project.add_event_to_log(f"Задача {task.id} отредактирована", current_user)  ## Журналирование
    db.session.commit()

    return redirect(url_for('task_manager.project', project_id=project_id))


@task_manager_bp.route('/project/<int:project_id>/comment/<int:task_id>', methods=['POST'], endpoint='comment')
@login_required
def create_task_comment(project_id, task_id):
    project = Project.query.get(project_id)
    task = Task.query.get(task_id)
    current_user_id = User.query.get(session.get('user_id')).id
    members = project.get_active_members_ids()

    if project is None or task is None:
        return jsonify({"message": "Проект или задача не найдены"}), 404

    # Проверяем доступ
    if current_user_id in members:
        comment_text = request.form.get('comment_text')
    else:
        return jsonify({"message": "У вас нет доступа к этому проекту"}), 403

    if comment_text:
        new_comment = TaskComment(text=comment_text, task_id=task_id)
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({"message": "Комментарий успешно добавлен"}), 201
    else:
        return jsonify({"message": "Некорректный комментарий"}), 400


@task_manager_bp.route('/project/<int:project_id>/delete_task/<int:task_id>', methods=['POST'], endpoint='delete_task')
@login_required
def delete_task(project_id, task_id):
    project = Project.query.get(project_id)
    task = Task.query.get(task_id)
    current_user = User.query.get(session.get('user_id'))
    project.add_event_to_log(f'Удалена задача: {task.name}', current_user)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('task_manager.project', project_id=project_id))


@task_manager_bp.route('/update_status/<int:project_id>/<int:task_id>/<string:new_status>', methods=['POST'], endpoint='change_task_status')
@login_required
def change_task_status(project_id, task_id, new_status):
    current_user_id = User.query.get(session.get('user_id')).id
    project = Project.query.get(project_id)
    task = Task.query.get(task_id)
    members = project.get_active_members_ids()

    if current_user_id in members:
        task.status = new_status
        current_user = User.query.get(session['user_id'])
        project.add_event_to_log(f"Изменен статус задачи {task.id} - {task.name}", current_user)  ## Журналирование
        db.session.commit()
        return jsonify({'message': 'Статус успешно изменен.'}), 200
    else:
        return jsonify({'message': 'У вас нет прав для изменения статуса.'}), 403


@task_manager_bp.route('/update_status_devflow/<int:project_id>/<int:task_id>/<string:new_status>', methods=['POST'], endpoint='change_devflow_task_status')
@login_required
def change_devflow_task_status(project_id, task_id, new_status):
    current_user_id = User.query.get(session.get('user_id')).id
    project = Project.query.get(project_id)
    task = Task.query.get(task_id)
    members = project.get_active_members_ids()

    if current_user_id in members:
        task.status = new_status

        current_user = User.query.get(session['user_id'])
        project.add_event_to_log(f"Изменен статус задачи {task.id} - {task.name}", current_user)  ## Журналирование
        db.session.commit()
        task_status_abbreviated = status_abbreviate(task.status)
        return jsonify({'message': 'Статус успешно изменен.', 'task_status': task_status_abbreviated}), 200
    else:
        return jsonify({'message': 'У вас нет прав для изменения статуса.'}), 403


### РОУТЫ ПРИГЛАШЕНИЙ


@task_manager_bp.route('/project/<int:project_id>/invite', methods=['GET', 'POST'], endpoint='invite')
@login_required
def invite_to_project(project_id):
    project = Project.query.get(project_id)
    current_user_id = User.query.get(session.get('user_id')).id

    tm_invite_form = InviteCreationForm()

    if project.owner != current_user_id:
        return jsonify({'status': 'error', 'message': 'Только владелец проекта может приглашать пользователей.'})

    if tm_invite_form.validate_on_submit():
        recipient_email = tm_invite_form.recipient.data
        recipient_user = User.query.filter_by(email=recipient_email).first()
        if project.type == 'basic':
            role = 'basic'
        else:
            role = tm_invite_form.role.data

        if not recipient_user:
            return jsonify({'status': 'error', 'message': 'Пользователь с указанным адресом электронной почты не найден.'})

        invitation = Invitation.query.filter_by(project_id=project_id, received_by_id=recipient_user.id).first()
        if invitation:
            return jsonify({'status': 'error', 'message': 'Этот пользователь уже приглашен в проект.'})

        new_invitation = Invitation(sent_by_id=current_user_id, received_by_id=recipient_user.id, project_id=project_id, role=role)
        db.session.add(new_invitation)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Приглашение успешно отправлено.'})

    return jsonify({'status': 'error', 'message': 'Неверные данные формы.'})


@task_manager_bp.route('/project/<int:project_id>/remove_member/<int:member_id>', methods=['POST'], endpoint='remove_from_project')
@login_required
def remove_from_project(project_id, member_id):
    project = Project.query.get(project_id)
    current_user_id = User.query.get(session.get('user_id')).id

    if project.owner != current_user_id:
        return "Вы не являетесь владельцем проекта", 403

    member = User.query.get(member_id)
    if not member:
        return "Участник не найден", 404

    # Находим приглашение и удаляем его
    invitation = Invitation.query.filter_by(sent_by_id=project.owner, received_by_id=member_id, project_id=project.id).first()
    if invitation:
        current_user = User.query.get(session['user_id'])
        project.remove_member_role(member.id)
        project.add_event_to_log(f"Пользователь {member.username} удален из проекта", current_user)  ## Журналирование
        db.session.delete(invitation)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Участник успешно исключен из проекта'})
    else:
        return jsonify({'status': 'error', 'message': 'При исключении участника произошла ошибка'})


@task_manager_bp.route('/accept-invitation/<int:invitation_id>', methods=['POST'], endpoint='accept_invitation')
@login_required
def accept_invitation(invitation_id):
    invitation = Invitation.query.get(invitation_id)
    if not invitation:
        return jsonify({'message': 'Приглашение не найдено. Странно, да?'}), 200

    invitation.accept()
    user = User.query.get(invitation.received_by_id)
    user_id = user.id
    username = user.username
    role = invitation.role
    project = Project.query.get(invitation.project_id)
    # Обновите поле members_roles проекта
    members_roles = project.members_roles or []
    members_roles.append((user_id, username, role))
    project.members_roles = members_roles
    db.session.commit()

    return jsonify({'message': 'Приглашение подтверждено.'}), 200


@task_manager_bp.route('/reject-invitation/<int:invitation_id>', methods=['POST'], endpoint='reject_invitation')
@login_required
def reject_invitation(invitation_id):
    invitation = Invitation.query.get(invitation_id)
    if not invitation:
        return jsonify({'message': 'Приглашение не найдено. Странно, да?'}), 200

    invitation.reject()

    return jsonify({'message': 'Приглашение отклонено и удалено.'}), 200
