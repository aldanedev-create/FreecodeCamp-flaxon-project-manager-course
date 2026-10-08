"""Maintain exact file replacements for the generated-project teaching sequence."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
FINAL=(ROOT/'app.py').read_text()

def factory(stage):
    if stage >= 13:
        return FINAL
    text=FINAL
    for name,path,level in [('auth','auth',4),('projects','projects',5),('tasks','tasks',6),('content','content',13)]:
        if stage < level:
            text=text.replace(f'from modules.{path}.module import {name}\n','')
            text=text.replace(f'        ({name}, "/api/{path}"),\n','')
    if stage < 12:
        text=text.replace('from backoffice import configure_backoffice\n','')
        text=re.sub(r'    configure_backoffice\(.*?\n    \)\n','',text,flags=re.S)
    if stage < 4:
        text=text.replace('from argon2 import PasswordHasher\n','')
        text=text.replace('    app.hasher = PasswordHasher()\n','').replace('    app.dummy_password_hash = app.hasher.hash("dummy-password-for-timing-only")\n','')
    if stage < 3:
        text=text.replace('from database import Database\n','').replace('    app.course_db = Database(database_path or DATABASE_PATH)\n','')
        text=text.replace('        await app.course_db.one("SELECT 1 FROM users LIMIT 1")\n','')
    if stage < 8:
        text=re.sub(r'    app.use_teloce\(.*?\n    \)\n','',text,flags=re.S)
        begin=text.index('    # Explicit shell routes')
        end=text.index('    return app',begin)
        text=text[:begin]+'''    @app.get("/")
    async def home():
        return {"data": {"message": "Backend lesson ready. The SPA starts in chapter 8."}}

'''+text[end:]
    else:
        for route in ['/help','/help/<slug>']:
            text=text.replace(f'    @app.get("{route}")\n','')
        if stage < 11:
            text=text.replace('    @app.get("/projects/<int:project_id>")\n','')
    return text

shell=(ROOT/'ui/app.html').read_text().replace('        <a href="/help" data-teloce-link>Help</a>\n','')
def placeholder(title,props=''):
    return f'''<template><section><h1>{title}</h1><p>This screen is built in the next UI lesson.</p></section></template>
<script lang="ts">export default {{{props}}};</script>
<style scoped>
h1 {{ font-size: 2rem; }}
p {{ line-height: 1.6; }}
</style>
'''
# Each chapter lists complete files. CREATE/EDIT is calculated against earlier steps.
files={
2:['settings.py','app.py'],
3:['database.py','migrations/0001_initial.json','management.py','app.py'],
4:['validation.py','security.py','modules/auth/__init__.py','modules/auth/module.py','app.py'],
5:['modules/projects/__init__.py','modules/projects/module.py','scripts/course_api_demo.py','app.py'],
6:['modules/tasks/__init__.py','modules/tasks/module.py','app.py'],
7:['tests/conftest.py','tests/test_api.py'],
8:['ui/types.ts','ui/api.ts','ui/app.html','ui/pages/Home.html','modules/auth/ui/pages/Login.html','modules/projects/ui/pages/ProjectList.html','modules/projects/ui/pages/ProjectDetails/[id].html','app.py'],
9:['modules/auth/ui/pages/Login.html','modules/projects/ui/pages/ProjectList.html'],
10:['modules/projects/ui/components/TaskForm.html','modules/projects/ui/components/TaskList.html','modules/projects/ui/pages/ProjectDetails/[id].html'],
11:['app.py'],
12:['backoffice.py','app.py'],
13:['modules/content/__init__.py','modules/content/module.py','modules/content/ui/pages/Help.html','modules/content/ui/pages/Article/[slug].html','seed.py','ui/app.html','app.py'],
14:['tests/test_backoffice.py','tests/test_cms_security.py','scripts/browser_smoke.py'],
15:['.env.example','scripts/build_ui.py','render.yaml']}
commands={
2:'python -m flaxon run app:app --reload\n# In a second terminal:\ncurl http://127.0.0.1:8000/api/welcome/status',
3:'python management.py migrate\npython management.py migrate --status\npython -m flaxon run app:app --reload',
4:'python -m flaxon run app:app --reload\n# In a second terminal:\ncurl -c cookies.txt http://127.0.0.1:8000/api/auth/session',
5:'python -m flaxon run app:app --reload\n# In a second terminal:\npython scripts/course_api_demo.py',
6:'python -m flaxon run app:app --reload\n# Exercise the task URLs shown in this chapter with your cookie and new CSRF token.',
7:'python -m pytest -q tests/test_api.py',
8:'python -m flaxon run app:app --reload\n# Open http://127.0.0.1:8000/\n# Account/project screens are placeholders until chapter 9.',
9:'python -m flaxon run app:app --reload\n# Open /login; register; create a project on /projects.\n# Project details are completed in chapter 10.',
10:'python -m flaxon run app:app --reload\n# Navigate to a project by its SPA link and add two tasks.\n# Direct detail-page refresh is added in chapter 11.',
11:'python -m flaxon run app:app --reload\n# Refresh a nested /projects/ID URL, then use Back and Forward.',
12:'python management.py setup-admin\npython -m flaxon run app:app --reload\n# Open /admin/login with the staff account you just created.',
13:'python management.py seed\n# Stop/restart the running server after seeding:\npython -m flaxon run app:app --reload\n# Open /help and /admin/cms/.',
14:'python -m playwright install chromium\npython -m pytest -q\npython scripts/browser_smoke.py\npython scripts/browser_smoke.py --production',
15:'python scripts/build_ui.py\npython -m pip check'}
existing={'app.py','settings.py','management.py','migrations/0001_initial.json','ui/app.html'}
steps=[]
for stage in range(2,16):
    entries=[]
    for path in files[stage]:
        content=factory(stage) if path=='app.py' else (ROOT/path).read_text()
        if stage==8:
            if path=='ui/app.html':content=shell
            elif path=='modules/auth/ui/pages/Login.html':content=placeholder('Account')
            elif path=='modules/projects/ui/pages/ProjectList.html':content=placeholder('Projects')
            elif path=='modules/projects/ui/pages/ProjectDetails/[id].html':content=placeholder('Project details',"props: ['id']")
        entries.append({'path':path,'action':'EDIT - replace the entire file' if path in existing else 'CREATE - make parent folders, then create this file','content':content})
        existing.add(path)
    steps.append({'chapter':stage,'files':entries,'commands':commands[stage],'delete':['migrations/0001_project_notes.json'] if stage==3 else []})
(ROOT/'course/build-steps.json').write_text(json.dumps(steps,indent=2)+'\n')
print('Generated exact build steps for chapters 2-15')
