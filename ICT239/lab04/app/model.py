from app import db

class Task(db.Document):
    task_id = db.IntField(required=True, unique=True)
    title = db.StringField(required=True, max_length=200)
    description = db.StringField(max_length=500)
    start_date = db.DateField()
    due_date = db.DateField()
    priority = db.StringField(required=True)

    meta = {
        'collection': 'tasks'
    }

    @staticmethod
    def get_task_by_id(task_id):
        return Task.objects(task_id=task_id).first()
    
    @staticmethod
    def delete_task_by_id(task_id):
        task = Task.get_task_by_id(task_id)
        if task:
            task.delete()
            return True
        return False
    
    @staticmethod
    def update_task(task_id, data):
        task = Task.get_task_by_id(task_id)
        if task:
            for key, value in data.items():
                setattr(task, key, value)
            task.save()
            return task
        return None
    
    @staticmethod
    def add_task(data):
        new_task = Task(**data)
        new_task.save()
        return new_task
    
    @staticmethod
    def get_all_tasks():
        return Task.objects()