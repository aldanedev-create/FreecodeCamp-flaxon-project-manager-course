"""Server compilation and explicit checking have separate responsibilities."""


def test_course_disables_background_checker(application):
    assert application.teloce.typecheck is False
    assert application.teloce.development_typecheck.task is None
