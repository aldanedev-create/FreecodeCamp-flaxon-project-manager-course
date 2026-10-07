# Sample lesson: one project API to a Teloce screen

Target: 12-15 minutes. Record with your own voice. This file is a rehearsal script,
not a completed recording. The finished app already contains the feature; use a
throwaway teaching checkout when removing code to type it again.

## Before recording

Install using the README, migrate, and run the development server. Register a
browser account. Close personal tabs, hide credentials, set the editor to a
readable font, and test your microphone. Capture 1080p if your equipment supports
it; prioritize legible code and clean audio. Keep decorative CSS already supplied.
Run `python scripts/course_api_demo.py` and the ownership test before the take.
The demo deliberately creates a new sample account and project on each run.

## 0:00-1:00 | Show the result

Say: "We will create a project through a protected Flaxon API, test its ownership
rule, then display it in a Teloce HTML screen. The browser cannot choose who owns
this project. The server gets that from the signed-in session."

Show /projects, create a project, and open it. Explain the JSON data envelope.

## 1:00-4:00 | Type the route

Open modules/projects/module.py. Type create_project while explaining each step:
check CSRF, require a user, parse a JSON object, validate name/description, insert
with SQL placeholders, return the owned record with 201. Show owned_project and
point to both the ID and owner_id conditions. Do not skip imports or pretend the
session/database helper has not been supplied by earlier chapters.

Say: "A name in a request is a value. A question mark lets SQLite treat it as a
value instead of SQL. The session decides owner_id."

## 4:00-6:00 | Exercise HTTP

In a second terminal run `python scripts/course_api_demo.py`. Show the created
record and the 400 for a blank name. Explain that registration rotates CSRF;
the demo reads the new token before creating the project. Its account is separate
from your browser account.

## 6:00-8:00 | Test ownership

Open tests/test_api.py and explain test_project_crud_and_ownership: create one
project, register a different user, and expect 404 for read/update/delete. Run:

```bash
python -m pytest -q tests/test_api.py -k project_crud_and_ownership
```

Say: "A hidden button cannot protect data. This test calls the API directly as
another user. The server must deny it."

## 8:00-12:00 | Connect the screen

Open modules/projects/ui/pages/ProjectList.html. Explain the api import, mounted
GET request, projects array, loading/error messages, and v-for cards. Type the
createProject method and form submit binding. The helper unwraps data and sends
cookies plus CSRF. On success prepend the returned project and clear the fields.
Show the busy guard and finally block so failure does not leave the button stuck.

Explain `data-teloce-link`: an anchor to /projects/ID mounts the module page
inside the SPA shell. A direct refresh also needs the Python shell route.
Create a project in your browser, then use Back and refresh its detail page.

## 12:00-15:00 | Recap and exercise

Ask the viewer to submit a whitespace-only name through the API and add a test.
Recap the path: form -> api helper -> Flaxon route -> owned database row -> JSON
-> reactive screen. Mention that task signals and Admin/CMS follow in later lessons.

## Feedback before recording the full course

Share the sample with two or three learners. Ask where they first became confused,
which command they could not reproduce, and whether the font/audio were clear.
Record timestamps, then revise the script and chapter before re-recording. Approval
for YouTube publication is a separate decision by freeCodeCamp.

For each full-course chapter: show the goal, type meaningful behavior, demonstrate
a success and a failure, run the relevant check, and point to the checkpoint.
Avoid recording installation waits. End deployment with persistence and denied
request checks rather than only a service-success screen.
