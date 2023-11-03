from .models import Project

projects = Project.query.all()

# Вывести тип каждого проекта
for project in projects:
    print(f"Project ID: {project.id}, Name: {project.name}, Type: {project.type}")