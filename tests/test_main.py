import types
import unittest
from unittest.mock import patch

from main import cleanup_iteration_pages, finalize_finished_course, detect_user_id, load_learned_courses


class DetailPage:
    def __init__(self, url, course_key=None):
        self.url = url
        if course_key is not None:
            self._course_key = course_key


class UserPage:
    def __init__(self, text):
        self.text = text

    class Body:
        def __init__(self, text):
            self.text = text
        def inner_text(self):
            return self.text

    def locator(self, selector):
        return self.Body(self.text)


class OwnedPage:
    def __init__(self, url):
        self.url = url
        self.closed = False

    def close(self):
        self.closed = True


class MainFlowTests(unittest.TestCase):
    @patch("main.remember_course")
    def test_unfinished_video_is_not_recorded(self, remember):
        detail = DetailPage("https://learning.example/#/CourseInfo?courseid=123")
        with self.assertRaises(RuntimeError):
            finalize_finished_course(detail, set(), video_finished=False)
        remember.assert_not_called()

    def test_detect_user_id_from_welcome_text(self):
        self.assertEqual(detect_user_id(UserPage("欢迎您，测试用户！")), "测试用户")

    @patch("main.remember_course")
    def test_finished_course_prefers_url_course_id(self, remember):
        detail = DetailPage(
            "https://learning.example/#/CourseInfo?courseid=123",
            course_key="title:fallback|duration:12",
        )
        learned = set()
        self.assertEqual(finalize_finished_course(detail, learned, video_finished=True), "123")
        remember.assert_called_once_with("123", learned)

    def test_cleanup_keeps_owned_pages(self):
        course_page = OwnedPage("https://learning.example/#/Course")
        credit_page = OwnedPage("https://learning.example/#/backIndex")
        detail_page = OwnedPage("https://learning.example/#/CourseInfo")
        context = types.SimpleNamespace(pages=[course_page, credit_page, detail_page])

        cleanup_iteration_pages(context, {course_page, credit_page})

        self.assertFalse(course_page.closed)
        self.assertFalse(credit_page.closed)
        self.assertTrue(detail_page.closed)


if __name__ == "__main__":
    unittest.main()
