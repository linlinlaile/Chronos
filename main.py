"""刷课时脚本 - 主入口（常驻循环模式）

浏览器启动后保持打开，登录一次后持续运行：
  读取学时缺口 → 选缺口最大的类别 → 进入课程页选类别 → 查询
  → 随机选课 → 播放 → 等学完 → 关闭播放页 → 回到循环
直到所有类别学时达标。

运行方式：python -u main.py
按 Ctrl+C 停止。
"""

import json
import os
import tempfile
from pathlib import Path

from browser import launch_browser, ensure_course_page, wait_for_login, goto_url
from actions import (
    select_course_category,
    click_query,
    collect_course_catalog,
    enter_catalog_course,
    click_learn_now,
    click_play_and_hold,
    dismiss_dialogs_all,
    wait_and_dismiss_dialogs,
    read_credit_data,
    choose_category_to_study,
    wait_video_finish,
    normalize_course_record,
    filter_credit_candidates,
    select_course_combination,
    rank_by_credit_efficiency,
    course_key_from_url,
    CourseCatalogEntryNotFoundError,
)
from config import (
    TARGET_URL,
    CREDIT_SYSTEM_URL,
    ENTER_CREDIT_SYSTEM,
    BACK_TO_LEARNING,
    KEEP_BROWSER_OPEN,
    CREDIT_CHECK_INTERVAL,
    RANDOM_PAGE_COUNT,
    LEARNED_COURSES_FILE,
    COURSE_CATALOG_FILE,
    COURSE_PAGE_END,
    TIMEOUT,
    MAX_COURSE_ATTEMPTS,
    CREDIT_SELECTION_MAX_CANDIDATES,
    CREDIT_REQUIREMENTS,
)

LEARNED_COURSES_PATH = Path(__file__).resolve().parent / LEARNED_COURSES_FILE
COURSE_CATALOG_PATH = Path(__file__).resolve().parent / COURSE_CATALOG_FILE
CURRENT_USER_ID = None


def detect_user_id(page) -> str | None:
    """Extract the logged-in display name from the authenticated home page."""
    try:
        text = page.locator("body").inner_text()
    except Exception:
        return None
    match = __import__("re").search(r"欢迎您\s*[,，]?\s*([^！!\r\n，,]+)", text)
    return match.group(1).strip() if match else None


def load_learned_courses(user_id: str | None = None) -> set[str]:
    try:
        data = json.loads(LEARNED_COURSES_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return set(data) if user_id is None else set()
        users = data.get("users", {}) if isinstance(data, dict) else {}
        if user_id:
            return set(users.get(user_id, []))
        return set(data.get("courses", data.get("legacy", [])))
    except (FileNotFoundError, json.JSONDecodeError, AttributeError):
        return set()


def load_course_catalog() -> dict[str, list[dict]]:
    try:
        data = json.loads(COURSE_CATALOG_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {
            category: [normalize_course_record(record, category) for record in records]
            for category, records in data.items()
            if isinstance(records, list)
        }
    except (FileNotFoundError, json.JSONDecodeError, AttributeError):
        return {}


def save_course_catalog(catalog: dict[str, list[dict]]) -> None:
    payload = json.dumps(catalog, ensure_ascii=False, indent=2)
    fd, temp_name = tempfile.mkstemp(prefix="course_catalog.", suffix=".tmp", dir=COURSE_CATALOG_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, COURSE_CATALOG_PATH)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def remember_course(course_key: str, learned: set[str], user_id: str | None = None) -> None:
    if not course_key or course_key in learned:
        return
    learned.add(course_key)
    existing = {}
    try:
        loaded = json.loads(LEARNED_COURSES_PATH.read_text(encoding="utf-8"))
        existing = {"legacy": loaded} if isinstance(loaded, list) else loaded
    except (FileNotFoundError, json.JSONDecodeError, AttributeError):
        pass
    if user_id:
        existing.setdefault("users", {})[user_id] = sorted(learned)
        existing.pop("courses", None)
    else:
        existing["courses"] = sorted(learned)
    LEARNED_COURSES_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已记录完成课程: {course_key}")


def finalize_finished_course(detail_page, learned: set[str], video_finished: bool, user_id: str | None = None) -> str:
    """视频真实播放结束后持久化课程，成功弹窗作为可选确认。"""
    if not video_finished:
        raise RuntimeError("视频未确认播放完成，课程不会记录为已完成")
    url_key = course_key_from_url(detail_page.url)
    key = (
        url_key
        if url_key and url_key != detail_page.url
        else getattr(detail_page, "_course_key", None)
    )
    if not key:
        raise RuntimeError("课程已确认完成，但无法读取稳定课程标识")
    if user_id is None:
        remember_course(key, learned)
    else:
        remember_course(key, learned, user_id)
    return key


def cleanup_iteration_pages(context, retained_pages: set) -> None:
    """只关闭当前课程新建的详情和播放页。"""
    for candidate in list(context.pages):
        if candidate in retained_pages or "about:blank" in candidate.url:
            continue
        try:
            candidate.close()
        except Exception:
            pass


def enter_credit_system(page, context, credit_page=None):
    """点击「进入学时管理系统」进入学时系统首页。"""
    if credit_page is not None:
        try:
            if not credit_page.is_closed():
                credit_page.reload(wait_until="domcontentloaded", timeout=TIMEOUT)
                credit_page.wait_for_selector(".imgBox", timeout=15_000)
                credit_page.bring_to_front()
                print(f"已刷新学时管理系统: {credit_page.url}")
                return credit_page
        except Exception as exc:
            print(f"复用学时页面失败，将重新打开: {exc}")

    page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
    btn_selector = f"button:has-text('{ENTER_CREDIT_SYSTEM}')"
    btn = page.locator(btn_selector)
    try:
        # 登录回跳后的首页是 SPA；任意 button 出现不代表首页业务数据已经渲染。
        btn.first.wait_for(state="visible", timeout=20_000)
    except Exception:
        print("登录回跳后的课程首页尚未完成渲染，刷新后重试进入学时系统...")
        page.reload(wait_until="domcontentloaded", timeout=TIMEOUT)
        try:
            btn.first.wait_for(state="visible", timeout=20_000)
        except Exception as exc:
            raise RuntimeError("课程页未找到进入学时管理系统按钮，登录页面可能仍在刷新") from exc

    old_pages = set(context.pages)
    try:
        with context.expect_page(timeout=5000) as info:
            btn.first.click()
        credit_page = info.value
    except Exception:
        credit_page = next(
            (candidate for candidate in context.pages if candidate not in old_pages),
            page,
        )

    credit_page.bring_to_front()
    try:
        credit_page.wait_for_selector(".imgBox", timeout=15_000)
    except Exception:
        credit_page.wait_for_timeout(1000)
    for candidate in context.pages:
        if candidate.locator(".imgBox").count() > 0:
            candidate.bring_to_front()
            print(f"已进入学时管理系统: {candidate.url}")
            return candidate
    raise RuntimeError("未找到学时管理系统页面，未读取学时")


def back_to_course_page(page) -> None:
    """从学时系统返回课程页。"""
    # 学时系统有「进入在线学习系统」按钮，或直接导航
    btn = page.locator(f"button:has-text('{BACK_TO_LEARNING}')")
    if "#/Course" not in page.url and btn.count() > 0:
        btn.first.click()
    if "#/Course" not in page.url:
        goto_url(page, TARGET_URL)
    page.wait_for_selector(".selectList", timeout=15_000)


def main() -> None:
    context = None
    page = None

    try:
        # 1. 启动浏览器（保持打开，不关闭）
        playwright, context, page = launch_browser()

        # 1.5 先导航到课程页
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("button", timeout=15_000)

        # 2. 等待登录
        page = wait_for_login(page, context)
        user_id = detect_user_id(page)
        if user_id:
            print(f"检测到登录用户: {user_id}")
        else:
            print("未读取到用户标识，使用兼容的共享学习记录")

        # 3. 常驻循环
        round_num = 0
        credit_data = None
        category = None
        credit_page = None
        learned_courses = load_learned_courses(user_id)
        course_catalog = load_course_catalog()
        failed_courses = set()
        print(f"已加载 {len(learned_courses)} 门已完成课程记录")
        courses_since_credit_check = CREDIT_CHECK_INTERVAL
        while True:
            round_num += 1
            print(f"\n===== 第 {round_num} 轮学习 =====")

            # 只在启动和达到检查间隔后刷新学时，避免每门课都切回学时页。
            if credit_data is None or courses_since_credit_check >= CREDIT_CHECK_INTERVAL:
                credit_page = enter_credit_system(page, context, credit_page)
                credit_data = read_credit_data(credit_page)
                category = choose_category_to_study(credit_data)
                courses_since_credit_check = 0
                if category is None:
                    print("\n*** 所有类别学时均已达标！任务完成！ ***")
                    break
            else:
                category_catalog = sorted(
                    category_catalog,
                    key=lambda record: (
                        record.get("duration", 9999),
                        record.get("page", 0),
                        record.get("position", 0),
                    ),
                )
                course_catalog[category] = category_catalog
                print(
                    f"本轮继续学习「{category}」，暂不刷新学时面板 "
                    f"（{courses_since_credit_check}/{CREDIT_CHECK_INTERVAL}）"
                )

            # 3.3 返回课程页，选择类别，查询
            back_to_course_page(page)
            select_course_category(page, category)
            dismiss_dialogs_all(context)
            click_query(page)
            dismiss_dialogs_all(context)

            category_catalog = course_catalog.get(category)
            if not category_catalog:
                print(f"首次扫描「{category}」课程第 1 至第 {COURSE_PAGE_END} 页...")
                category_catalog = collect_course_catalog(page, COURSE_PAGE_END, category)
                course_catalog[category] = category_catalog
                save_course_catalog(course_catalog)
            else:
                # 旧目录可能只有视频时长，没有卡片上的可计学时；先补全元数据，
                # 避免降级到“只选最短视频”而错过更高性价比课程。
                known_credit_count = sum(
                    1 for record in category_catalog
                    if normalize_course_record(record, category).get("credit_hours") is not None
                )
                if known_credit_count == 0:
                    print(f"检测到「{category}」课程目录缺少学时字段，重新扫描以补全性价比数据...")
                    refreshed_catalog = collect_course_catalog(page, COURSE_PAGE_END, category)
                    if refreshed_catalog:
                        category_catalog = refreshed_catalog
                        course_catalog[category] = refreshed_catalog
                        save_course_catalog(course_catalog)
                print(
                    f"使用已保存的「{category}」课程目录，共 {len(category_catalog)} 门，"
                    "按时长顺序继续学习"
                )

            # 3.4-3.8 选择、播放并确认课程；单门失败时尝试本轮其他候选。
            completed = False
            attempt = 1
            catalog_refreshed = False
            while attempt <= MAX_COURSE_ATTEMPTS:
                detail_page = None
                next_course = None
                try:
                    candidates = filter_credit_candidates(
                        category_catalog, learned_courses, failed_courses, category
                    )
                    gap = CREDIT_REQUIREMENTS[category] - credit_data.get("completed", {}).get(category, 0)
                    plan = select_course_combination(candidates, gap, CREDIT_SELECTION_MAX_CANDIDATES)
                    if plan:
                        print(
                            f"学时性价比选择: 预计 {sum(r.get('duration_minutes', 0) for r in plan)} 分钟，"
                            f"覆盖 {sum(r.get('credit_hours', 0) for r in plan):g} 学时"
                        )
                        next_course = plan[0]
                    else:
                        fallback = filter_credit_candidates(category_catalog, learned_courses, failed_courses, category)
                        next_course = next(iter(rank_by_credit_efficiency(fallback)), None)
                    if next_course is None:
                        raise RuntimeError(f"「{category}」课程目录中的课程均已学习或失败")
                    detail_page = enter_catalog_course(
                        page,
                        context,
                        next_course,
                        learned_courses | failed_courses,
                    )
                    # 目录位置可能因平台重新分页而被修复，立即持久化修复结果。
                    save_course_catalog(course_catalog)
                    click_learn_now(detail_page)
                    # 进入未完成课程时会异步弹出“是否继续学习”，选择“确定”。
                    dismiss_dialogs_all(context, timeout_sec=5)
                    play_page = click_play_and_hold(detail_page)

                    print("\n开始观看课程视频...")
                    finished = wait_video_finish(play_page)
                    if not finished:
                        raise RuntimeError("视频未确认播放完成")

                    confirmed = wait_and_dismiss_dialogs(context, timeout_sec=30)
                    if not confirmed:
                        print("视频已正常结束但未检测到学习成功弹框，仍记录本地完成状态")
                    completed_key = finalize_finished_course(
                        detail_page, learned_courses, finished, user_id
                    )
                    # The catalog key is usually title+duration while the detail
                    # URL yields a numeric course id. Persist both aliases so a
                    # later catalog reload still excludes this completed course.
                    catalog_key = next_course.get("key")
                    if catalog_key and catalog_key != completed_key:
                        remember_course(catalog_key, learned_courses, user_id)
                        next_course["course_id"] = completed_key
                        save_course_catalog(course_catalog)
                    completed = True
                    break
                except Exception as exc:
                    retained_pages = {page}
                    if credit_page is not None:
                        try:
                            if not credit_page.is_closed():
                                retained_pages.add(credit_page)
                        except Exception:
                            pass
                    cleanup_iteration_pages(context, retained_pages)

                    if (
                        isinstance(exc, CourseCatalogEntryNotFoundError)
                        and not catalog_refreshed
                    ):
                        print(
                            "检测到保存的课程目录已经过期，重新扫描当前类别第 "
                            f"1 至第 {COURSE_PAGE_END} 页..."
                        )
                        try:
                            back_to_course_page(page)
                            select_course_category(page, category)
                            click_query(page)
                            category_catalog = collect_course_catalog(page, COURSE_PAGE_END, category)
                            if not category_catalog:
                                raise RuntimeError("重新扫描后没有找到可用课程")
                            course_catalog[category] = category_catalog
                            save_course_catalog(course_catalog)
                            catalog_refreshed = True
                            print(
                                f"课程目录已重建，共 {len(category_catalog)} 门，"
                                "继续选择下一门课程"
                            )
                            continue
                        except Exception as refresh_exc:
                            raise RuntimeError(
                                f"课程目录过期且自动重建失败: {refresh_exc}"
                            ) from refresh_exc

                    failed_key = None
                    if detail_page is not None:
                        failed_key = getattr(detail_page, "_course_key", None)
                        if not failed_key:
                            failed_key = course_key_from_url(detail_page.url)
                    if failed_key:
                        failed_courses.add(failed_key)
                    if next_course and next_course.get("key"):
                        failed_courses.add(next_course["key"])
                    if attempt >= MAX_COURSE_ATTEMPTS:
                        raise RuntimeError(
                            f"连续 {MAX_COURSE_ATTEMPTS} 门课程失败，最后错误: {exc}"
                        ) from exc
                    print(
                        f"本门课程失败（第 {attempt}/{MAX_COURSE_ATTEMPTS} 次尝试）：{exc}"
                        "，准备选择下一门"
                    )
                    try:
                        back_to_course_page(page)
                        select_course_category(page, category)
                        click_query(page)
                    except Exception as recovery_exc:
                        raise RuntimeError(
                            f"课程失败后恢复课程列表失败: {recovery_exc}; 原始错误: {exc}"
                        ) from recovery_exc
                    attempt += 1

            if not completed:
                raise RuntimeError("本轮没有确认完成任何课程")
            courses_since_credit_check += 1

            retained_pages = {page}
            if credit_page is not None:
                try:
                    if not credit_page.is_closed():
                        retained_pages.add(credit_page)
                except Exception:
                    pass
            cleanup_iteration_pages(context, retained_pages)
            print(f"第 {round_num} 轮学习完成，准备下一轮...\n")

    except KeyboardInterrupt:
        print("\n用户中断，停止刷课。")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        try:
            if page:
                page.screenshot(path="error_screenshot.png", full_page=True)
        except Exception:
            pass
    finally:
        if context and KEEP_BROWSER_OPEN:
            print("浏览器保持打开，按 Ctrl+C 结束脚本。")
            try:
                while context.pages:
                    context.pages[0].wait_for_timeout(1000)
            except KeyboardInterrupt:
                print("脚本已停止，浏览器窗口保持打开。")
        elif context:
            context.close()


if __name__ == "__main__":
    main()
