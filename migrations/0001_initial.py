from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='AuthAttempt',
            fields=[
                ('key', fields.CharField(primary_key=True, unique=True, db_index=True, max_length=64)),
                ('attempts', fields.IntField(default=0)),
                ('started_at', fields.BigIntField(db_index=True)),
            ],
            options={'table': 'auth_attempts', 'app': 'models', 'pk_attr': 'key'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='User',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(max_length=80)),
                ('email', fields.CharField(unique=True, max_length=254)),
                ('password_hash', fields.TextField(unique=False)),
            ],
            options={'table': 'users', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Project',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('owner', fields.ForeignKeyField('models.User', source_field='owner_id', db_constraint=True, to_field='id', related_name='projects', on_delete=OnDelete.CASCADE)),
                ('name', fields.CharField(max_length=120)),
                ('description', fields.TextField(default='', unique=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'projects', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Session',
            fields=[
                ('token_hash', fields.CharField(primary_key=True, unique=True, db_index=True, max_length=64)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', null=True, db_constraint=True, to_field='id', on_delete=OnDelete.CASCADE)),
                ('csrf', fields.CharField(max_length=64)),
                ('expires_at', fields.BigIntField(db_index=True)),
            ],
            options={'table': 'sessions', 'app': 'models', 'pk_attr': 'token_hash'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Task',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('project', fields.ForeignKeyField('models.Project', source_field='project_id', db_constraint=True, to_field='id', related_name='tasks', on_delete=OnDelete.CASCADE)),
                ('title', fields.CharField(max_length=200)),
                ('status', fields.CharField(default='todo', max_length=10)),
                ('due_date', fields.DateField(null=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'tasks', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
