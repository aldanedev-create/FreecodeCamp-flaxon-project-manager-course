## Start here: create the project with the CLI

Use Python 3.12. Run the first commands in a new parent directory, not inside the
finished course repository. The reference checkout supplies the pinned course
wheels; you will write application code yourself in the generated project.

```bash
git clone https://github.com/aldanedev-create/FreecodeCamp-flaxon-project-manager-course.git course_reference
python -m venv course_env
```

Activate the bootstrap environment on Windows PowerShell:

```powershell
.\course_env\Scripts\Activate.ps1
```

Or activate it on macOS/Linux:

```bash
source course_env/bin/activate
```

Install while inside the reference folder so the relative wheel paths resolve:

```bash
cd course_reference
python -m pip install -r requirements-dev.txt
cd ..
flaxon new project_manager
cd project_manager
```

The CLI creates the project and its own `.venv`. Activate that project environment
now (rather than keeping the parent environment for the rest of the course).

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

## CREATE: prepare_course.py

Create this file in the generated project. It copies dependency files only; it
does not copy the completed application's Python or UI code.

```python
from pathlib import Path
import shutil

reference = Path("../course_reference")
if not reference.is_dir():
    raise SystemExit("Keep course_reference beside project_manager.")

shutil.copytree(reference / "vendor", "vendor", dirs_exist_ok=True)
for name in ("requirements.txt", "requirements-dev.txt", "requirements.lock.txt"):
    shutil.copy2(reference / name, name)

Path("scripts").mkdir(exist_ok=True)
shutil.copy2(reference / "scripts/verify_vendor.py", "scripts/verify_vendor.py")
print("Pinned course dependencies are ready; application code is still the starter.")
```

## Run these commands now

```bash
python prepare_course.py
python scripts/verify_vendor.py
python -m pip install -r requirements-dev.txt
python -m flaxon welcome
python -m flaxon welcome-status
python -m flaxon run app:app --reload
```

Open http://127.0.0.1:8000/. Show the welcome screen and click its Python API button.
Do not set up staff or run the generated migration yet. Chapter 3 supplies the
course migration and uses a fresh course database directory.

## What to say and show at this point

Say: "We generated the starter ourselves. The dependency helper copied wheels
and version pins, not the finished task manager. Next we will build the backend
one module at a time. The customer SPA returns in chapter 8."

Show: the welcome module, `flaxon_cli.py`, `management.py`, and `ui/app.html`.
Explain that the generated starter has its own CSS file; chapter 8 replaces the
shell and removes that file in favour of scoped component CSS.

Stop the server with Ctrl+C before chapter 2. Do not create a nested
project_manager directory by running the generation command again inside it.
