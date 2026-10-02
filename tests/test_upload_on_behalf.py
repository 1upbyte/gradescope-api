"""Unit tests for uploading a submission on behalf of a student."""

from io import BytesIO

from gradescopeapi.classes.upload import upload_assignment


class FakeResponse:
    def __init__(self, *, text: str = "", url: str = "") -> None:
        self.text = text
        self.url = url


class FakeSession:
    def __init__(self) -> None:
        self.post_body: bytes | None = None

    def get(self, _url: str) -> FakeResponse:
        return FakeResponse(text='<meta name="csrf-token" content="csrf-token">')

    def post(self, _url: str, *, data, headers) -> FakeResponse:
        assert headers["Content-Type"].startswith("multipart/form-data;")
        self.post_body = data.to_string()
        return FakeResponse(url="https://www.gradescope.com/submissions/123")


def make_submission() -> BytesIO:
    submission = BytesIO(b"print('hello')\n")
    submission.name = "answer.py"
    return submission


def test_upload_includes_owner_id_when_student_id_is_provided() -> None:
    session = FakeSession()

    result = upload_assignment(session, "1", "2", make_submission(), student_id="42")

    assert result == "https://www.gradescope.com/submissions/123"
    assert session.post_body is not None
    assert b'name="submission[owner_id]"\r\n\r\n42\r\n' in session.post_body


def test_upload_omits_owner_id_when_student_id_is_not_provided() -> None:
    session = FakeSession()

    result = upload_assignment(session, "1", "2", make_submission())

    assert result == "https://www.gradescope.com/submissions/123"
    assert session.post_body is not None
    assert b'name="submission[owner_id]"' not in session.post_body
