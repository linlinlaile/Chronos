import sys
import types
import unittest
from unittest.mock import MagicMock, patch


try:
    import playwright.sync_api  # noqa: F401
except ModuleNotFoundError:
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.Page = object
    sync_api.BrowserContext = object
    playwright = types.ModuleType("playwright")
    playwright.sync_api = sync_api
    sys.modules["playwright"] = playwright
    sys.modules["playwright.sync_api"] = sync_api


from actions import (  # noqa: E402
    _parse_credit_block,
    _check_page_dialogs,
    _dismiss_normal_dialogs,
    _dismiss_playback_interruption_dialogs,
    choose_category_to_study,
    click_learn_now,
    click_play_and_hold,
    parse_duration,
    _visible_course_page_locator,
    wait_and_dismiss_dialogs,
    wait_video_finish,
    parse_credit_hours,
    normalize_course_record,
    select_course_combination,
    filter_credit_candidates,
    rank_by_credit_efficiency,
)


class FakeLocator:
    def __init__(self, texts=None, count=None):
        self.texts = texts or []
        self._count = len(self.texts) if count is None else count
        self.first = self

    def count(self):
        return self._count

    def all_inner_texts(self):
        return self.texts

    def inner_text(self):
        return self.texts[0] if self.texts else ""

    def get_attribute(self, _name):
        return None

    def nth(self, index):
        return FakeLocator([self.texts[index]])


class FakeItem:
    def __init__(self, duration):
        self.duration = duration

    def locator(self, selector):
        if selector == ".Line2-item":
            return FakeLocator([f"时长：{self.duration} 分钟"])
        return FakeLocator(["课程"])


class FakePage:
    def __init__(self, video=False, fail_on_poll=False):
        self.video = video
        self.fail_on_poll = fail_on_poll
        self.url = "https://learning.example/#/class"
        self.context = types.SimpleNamespace(pages=[self])
        self.frames = []
        self.main_frame = None
        self.polls = 0

    def locator(self, selector):
        if selector == "video":
            return FakeLocator(count=1 if self.video else 0)
        return FakeLocator(count=0)

    def wait_for_timeout(self, _milliseconds):
        self.polls += 1

    def evaluate(self, script):
        if "window.__video_progress =" in script:
            return None
        if "return v ?" in script:
            return {"paused": False, "current": 1, "duration": 10}
        if self.fail_on_poll:
            raise RuntimeError("page closed")
        return {"ended": True, "current": 10, "duration": 10}

    def screenshot(self, **_kwargs):
        return None


class OnlineCheckPage(FakePage):
    def __init__(self):
        super().__init__(video=True)
        self.states = [
            {"paused": False, "ended": False, "current": 1, "duration": 10,
             "playbackRate": 1, "readyState": 4, "error": None},
            {"paused": True, "ended": False, "current": 5, "duration": 10,
             "playbackRate": 1, "readyState": 4, "error": None},
            {"paused": False, "ended": True, "current": 10, "duration": 10,
             "playbackRate": 1, "readyState": 4, "error": None},
        ]

    def evaluate(self, _script):
        return self.states.pop(0)


class FakeButton:
    def __init__(self, visible):
        self.visible = visible
        self.clicked = False

    def is_visible(self):
        return self.visible

    def is_enabled(self):
        return True

    def inner_text(self):
        return "立即学习"

    def click(self):
        self.clicked = True


class HiddenButtonPage(FakePage):
    def __init__(self):
        super().__init__()
        self.buttons = [FakeButton(False), FakeButton(True)]

    def wait_for_selector(self, _selector, **_kwargs):
        raise RuntimeError("visible selector unavailable in fallback fixture")

    def locator(self, selector):
        if selector == "button":
            return FakeButtonCollection(self.buttons)
        return FakeLocator(count=0)


class FakeButtonCollection:
    def __init__(self, buttons):
        self.buttons = buttons

    def count(self):
        return len(self.buttons)

    def nth(self, index):
        return self.buttons[index]


class PaginationPage:
    def locator(self, selector):
        if "li.number:visible" in selector:
            return FakeLocator(["104", "105", "106", "107", "108"])
        if "aria-current" in selector or "is-active" in selector:
            return FakeLocator(["106"])
        return FakeLocator(count=0)


class ActionsTests(unittest.TestCase):
    def test_credit_hour_parser_and_unknown(self):
        self.assertEqual(parse_credit_hours("可计学时：1.5 学时"), 1.5)
        self.assertIsNone(parse_credit_hours("课程编号 123"))

    def test_legacy_record_normalization(self):
        record = normalize_course_record({"key": "x", "duration": 12}, "专业课程")
        self.assertEqual(record["duration_minutes"], 12)
        self.assertIsNone(record["credit_hours"])
        self.assertEqual(record["category"], "专业课程")

    def test_shortest_credit_combination(self):
        records = [
            {"key": "a", "duration_minutes": 15, "credit_hours": 0.5},
            {"key": "b", "duration_minutes": 20, "credit_hours": 1.0},
            {"key": "c", "duration_minutes": 30, "credit_hours": 1.5},
        ]
        self.assertEqual([r["key"] for r in select_course_combination(records, 1.5)], ["c"])

    def test_credit_candidates_exclude_unknown_and_completed(self):
        records = [
            {"key": "done", "duration_minutes": 10, "credit_hours": 1},
            {"key": "unknown", "duration_minutes": 10},
            {"key": "ok", "duration_minutes": 10, "credit_hours": 1},
        ]
        result = filter_credit_candidates(records, {"done"})
        self.assertEqual([r["key"] for r in result], ["unknown", "ok"])

    def test_plan_changes_when_credit_gap_changes(self):
        records = [
            {"key": "half", "duration_minutes": 10, "credit_hours": 0.5},
            {"key": "full", "duration_minutes": 25, "credit_hours": 1.0},
            {"key": "double", "duration_minutes": 50, "credit_hours": 2.0},
        ]
        self.assertEqual([r["key"] for r in select_course_combination(records, 0.5)], ["half"])
        self.assertEqual([r["key"] for r in select_course_combination(records, 1.0)], ["full"])

    def test_efficiency_fallback_prefers_more_credit_per_minute(self):
        records = [
            {"key": "slow", "duration_minutes": 40, "credit_hours": 1.0},
            {"key": "efficient", "duration_minutes": 20, "credit_hours": 1.0},
        ]
        self.assertEqual(rank_by_credit_efficiency(records)[0]["key"], "efficient")

    def test_combination_ranks_short_courses_before_catalog_bound(self):
        records = [
            {"key": f"long-{i}", "duration_minutes": 43, "credit_hours": 1.0, "page": i}
            for i in range(80)
        ]
        records.append({"key": "short", "duration_minutes": 30, "credit_hours": 1.0, "page": 99})
        self.assertEqual([r["key"] for r in select_course_combination(records, 1.0)], ["short"])
    def test_combined_public_requirement_is_ignored(self):
        result = _parse_credit_block({
            0: "专业课程60.0学时",
            1: "行业公需和一般公需科目不少于18.0学时",
            2: "行业公需30.0学时",
            3: "一般公需0.0学时",
        })
        self.assertEqual(result, {"专业课程": 60.0, "行业公需": 30.0, "一般公需": 0.0})

    def test_largest_gap_category(self):
        result = choose_category_to_study({
            "completed": {"专业课程": 0, "行业公需": 30, "一般公需": 0}
        })
        self.assertEqual(result, "专业课程")

    def test_visible_page_is_selected_by_exact_text(self):
        locator = _visible_course_page_locator(PaginationPage(), 107)
        self.assertIsNotNone(locator)
        self.assertEqual(locator.inner_text(), "107")

    def test_missing_learning_control_fails(self):
        with self.assertRaises(RuntimeError):
            click_learn_now(FakePage())

    def test_learning_click_skips_hidden_duplicate(self):
        page = HiddenButtonPage()
        self.assertTrue(click_learn_now(page))
        self.assertFalse(page.buttons[0].clicked)
        self.assertTrue(page.buttons[1].clicked)

    def test_missing_play_control_fails(self):
        with self.assertRaises(RuntimeError):
            click_play_and_hold(FakePage())

    def test_video_completion_is_success(self):
        self.assertTrue(wait_video_finish(FakePage(video=True), timeout_sec=1))

    def test_video_page_error_is_failure(self):
        self.assertFalse(wait_video_finish(FakePage(video=True, fail_on_poll=True), timeout_sec=1))

    def test_online_confirmation_does_not_fail_playback(self):
        page = OnlineCheckPage()
        with patch(
            "actions._dismiss_playback_interruption_dialogs",
            side_effect=[True, False],
        ):
            self.assertTrue(wait_video_finish(page, timeout_sec=10))

    def test_completion_dialog_is_confirmed(self):
        page = FakePage()
        context = types.SimpleNamespace(pages=[page])
        with patch("actions._check_page_dialogs", return_value=True):
            self.assertTrue(wait_and_dismiss_dialogs(context, timeout_sec=1))
        self.assertGreater(page.polls, 0)

    def test_credit_awarded_dialog_selects_no(self):
        page = MagicMock()
        dialog = MagicMock()
        no_button = MagicMock()
        dialog.count.return_value = 1
        dialog.first = dialog
        dialog.inner_text.return_value = "您的学习时间已达到要求，获得学分:0.50,是否继续学习?"
        no_button.count.return_value = 1
        no_button.first = no_button
        dialog.locator.return_value = no_button
        page.locator.return_value = dialog

        self.assertTrue(_check_page_dialogs(page))
        no_button.click.assert_called_once_with()

    def test_unfinished_course_dialog_selects_confirm(self):
        page = MagicMock()
        dialog = MagicMock()
        yes_button = MagicMock()
        dialog.count.return_value = 1
        dialog.first = dialog
        dialog.inner_text.return_value = "本课程尚未完成，是否继续学习?"
        yes_button.count.return_value = 1
        yes_button.first = yes_button
        dialog.locator.return_value = yes_button
        page.locator.return_value = dialog

        self.assertTrue(_dismiss_normal_dialogs(page))
        yes_button.click.assert_called_once_with()

    def test_continue_question_is_not_completion(self):
        page = MagicMock()
        dialog = MagicMock()
        dialog.count.return_value = 1
        dialog.first = dialog
        dialog.inner_text.return_value = "本课程尚未完成，是否继续学习?"
        page.locator.return_value = dialog

        self.assertFalse(_check_page_dialogs(page))

    def test_missing_completion_dialog_is_failure(self):
        context = types.SimpleNamespace(pages=[FakePage()])
        with patch("actions._check_page_dialogs", return_value=False):
            self.assertFalse(wait_and_dismiss_dialogs(context, timeout_sec=1))

    def test_normal_dialog_does_not_confirm_completion(self):
        context = types.SimpleNamespace(pages=[FakePage()])
        with (
            patch("actions._check_page_dialogs", return_value=False),
            patch("actions._dismiss_normal_dialogs", return_value=True),
        ):
            self.assertFalse(wait_and_dismiss_dialogs(context, timeout_sec=1))

if __name__ == "__main__":
    unittest.main()
