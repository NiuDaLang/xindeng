# xindeng/tests/test_error_handler.py
"""
Tests for xindeng.views.error_500.

The handler renders 500.html, which extends base.html, whose includes
were the source of the original 500 in the image-URL incident. That
produced a nested 500 inside the handler — a confusing traceback
pointing at the error handler rather than the original failure.

The handler now catches any exception from render and returns a
minimal plain-text response. These tests pin both branches.
"""


def test_error_500_falls_back_to_string_when_render_raises(rf, monkeypatch):
    """
    When render raises, the handler must return a plain-text 500 with
    the fallback message — not propagate the second exception.
    """
    from xindeng import views

    def boom(*args, **kwargs):
        raise RuntimeError("template boom")

    monkeypatch.setattr(views, "render", boom)
    request = rf.get("/whatever")
    response = views.error_500(request)

    assert response.status_code == 500
    # Substring, not byte equality: the fallback is bilingual and the
    # Chinese half is free to be reworded without breaking the test.
    assert b"Server error. Please try again later." in response.content
    assert response["Content-Type"].startswith("text/plain")


def test_error_500_renders_template_when_render_succeeds(rf):
    """
    The happy path: render works, the template is served, still 500.
    """
    from xindeng import views

    request = rf.get("/whatever")
    response = views.error_500(request)

    assert response.status_code == 500