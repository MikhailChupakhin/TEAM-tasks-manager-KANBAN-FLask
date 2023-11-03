from sqlalchemy import PickleType
from sqlalchemy.orm import relationship, validates

from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
    username = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='author', lazy=True)
    invitations_sent = db.relationship('Invitation', backref='sent_by', foreign_keys='Invitation.sent_by_id', lazy=True)
    invitations_received = db.relationship('Invitation', backref='received_by', foreign_keys='Invitation.received_by_id',
                                           lazy=True)

    def __init__(self, email, password, username):
        self.email = email
        self.password = generate_password_hash(password)
        self.username = username

    def check_password(self, password):
        return check_password_hash(self.password, password)

### Модели Таск-менеджера


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(20), default='basic')

    tasks = db.relationship('Task', backref='project', lazy=True)
    invitations = db.relationship('Invitation', backref='project', lazy=True)

    members_roles = db.Column(PickleType)

    unattached_tasks_count = db.Column(db.Integer, default=0)
    active_tasks_count = db.Column(db.Integer, default=0)
    completed_tasks_count = db.Column(db.Integer, default=0)

    event_log = db.Column(db.Text)

    def __init__(self, name, description, owner, type, members_roles=None):
        self.name = name
        self.description = description
        self.owner = owner
        self.type = type
        self.members_roles = members_roles if members_roles is not None else []

    # Добавление новой связи между пользователем и его ролью в проекте
    def add_member_role(self, user_id, username, role):
        self.members_roles.append((user_id, username, role))

    # Удаление связи между пользователем и его ролью в проекте
    def remove_member_role(self, user_id):
        self.members_roles = [(uid, username, role) for uid, username, role in self.members_roles if uid != user_id]

    def get_active_members_ids(self):
        accepted_invitations = Invitation.query.filter_by(project_id=self.id, is_accepted=True).all()
        members = [invitation.received_by_id for invitation in accepted_invitations]
        members.append(self.owner)
        return members

    def get_members_choices(self):
        return [(user.id, user.username) for user in User.query.filter(User.id.in_(self.get_active_members_ids()))]

    def calculate_tasks_count(self):
        self.unattached_tasks_count = Task.query.filter_by(project_id=self.id, status='Ожидание').count()
        self.active_tasks_count = Task.query.filter_by(project_id=self.id, status='Выполняется').count()
        self.completed_tasks_count = Task.query.filter_by(project_id=self.id, status='Завершено').count()

    def add_event_to_log(self, event_text, user):
        current_datetime = datetime.now().strftime("%d.%m.%y %H:%M")
        log_entry = f"{current_datetime} {user.username}: {event_text}\n"
        self.event_log = log_entry if not self.event_log else self.event_log + log_entry


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sent_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    received_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_accepted = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(100), default='basic')

    def __init__(self, sent_by_id, received_by_id, project_id, role):
        self.sent_by_id = sent_by_id
        self.received_by_id = received_by_id
        self.project_id = project_id
        self.role = role

    def accept(self):
        self.is_accepted = True

    def reject(self):
        db.session.delete(self)
        db.session.commit()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    name = db.Column(db.String(150))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    basic_statuses = ['Ожидание', 'Выполняется', 'Завершено', 'Отменено']
    devflow_statuses = ['NEW', 'ASSIGNED', 'IN PROGRESS', 'NEED SOME INFO', 'DEPLOYING(TEST)',
                        'TESTING', 'TEST OK', 'TEST FAILED', 'DEPLOYING', 'DEPLOY FAILED',
                        'DEPLOY OK', 'STABILITY', 'REJECT', 'CLOSED']
    status = db.Column(db.String(100), default='Ожидание')
    deadline = db.Column(db.DateTime, nullable=True)
    responsible_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    responsible = relationship('User', foreign_keys=[responsible_id])
    comments = db.relationship('TaskComment', backref='task', lazy=True)
    comment_count = db.Column(db.Integer, default=0)

    def __init__(self, name, project_id, description, deadline=None, responsible=None):
        self.name = name
        self.project_id = project_id
        self.description = description
        project = Project.query.get(project_id)
        if project.type == 'basic':
            self.status = 'Ожидание'
        elif project.type == 'devflow':
            self.status = 'NEW'
        self.deadline = deadline
        self.responsible = responsible

    @validates('status')
    def validate_status(self, key, value):
        project = Project.query.get(self.project_id)

        if project.type == 'basic':
            allowed_statuses = self.basic_statuses
        elif project.type == 'devflow':
            allowed_statuses = self.devflow_statuses
        else:
            allowed_statuses = []

        if value not in allowed_statuses:
            raise ValueError(f"Invalid status: {value}. Allowed values are {', '.join(allowed_statuses)}")

        return value


class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    def __init__(self, text, task_id):
        self.text = text
        self.task_id = task_id
        task = Task.query.get(task_id)
        task.comment_count += 1

    @staticmethod
    def delete_comment(comment):
        # Уменьшаем счетчик комментариев для задачи
        task = Task.query.get(comment.task_id)
        task.comment_count -= 1

        db.session.delete(comment)


