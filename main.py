"""刷课时脚本 - 主入口（常驻循环模式）

浏览器启动后保持打开，登录一次后持续运行：
  读取学时缺口 → 选缺口最大的类别 → 进入课程页选类别 → 查询
  → 随机选课 → 播放 → 等学完 → 关闭播放页 → 回到循环
直到所有类别学时达标。

运行方式：python -u main.py
按 Ctrl+C 停止。
"""

from browser import launch_browser, ensure_course_page, wait_for_login, goto_url
from actions import (
    select_course_category,
    click_query,
    shortest_enter_course,
    click_learn_now,
    click_play_and_hold,
    dismiss_dialogs_all,
    read_credit_data,
    choose_category_to_study,
    wait_video_finish,
)
from config import TARGET_URL, CREDIT_SYSTEM_URL, ENTER_CREDIT_SYSTEM, BACK_TO_LEARNING


def enter_credit_system(page) -> None:
    """点击「进入学时管理系统」进入学时系统首页。"""
    page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    btn = page.locator(f"button:has-text('{ENTER_CREDIT_SYSTEM}')")
    if btn.count() > 0:
        btn.first.click()
        page.wait_for_timeout(6000)
        print(f"已进入学时管理系统: {page.url}")


def back_to_course_page(page) -> None:
    """从学时系统返回课程页。"""
    # 学时系统有「进入在线学习系统」按钮，或直接导航
    btn = page.locator(f"button:has-text('{BACK_TO_LEARNING}')")
    if btn.count() > 0:
        btn.first.click()
        page.wait_for_timeout(4000)
    # 确保在课程页
    goto_url(page, TARGET_URL)
    page.wait_for_timeout(4000)
    page.wait_for_selector(".selectList", timeout=15000)


def main() -> None:
    context = None
    page = None

    try:
        # 1. 启动浏览器（保持打开，不关闭）
        _, context, page = launch_browser()

        # 1.5 先导航到课程页
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(4000)

        # 2. 等待登录
        wait_for_login(page)

        # 3. 常驻循环
        round_num = 0
        while True:
            round_num += 1
            print(f"\n===== 第 {round_num} 轮学习 =====")

            # 3.1 进入学时系统，读取学时数据
            enter_credit_system(page)
            credit_data = read_credit_data(page)

            # 3.2 选择要学的类别
            category = choose_category_to_study(credit_data)
            if category is None:
                print("\n*** 所有类别学时均已达标！任务完成！ ***")
                break

            # 3.3 返回课程页，选择类别，查询
            back_to_course_page(page)
            select_course_category(page, category)
            dismiss_dialogs_all(context)
            click_query(page)
            dismiss_dialogs_all(context)

            # 3.4 选时长最短的课程进入
            detail_page = shortest_enter_course(page, context)

            # 3.5 立即学习
            click_learn_now(detail_page)
            dismiss_dialogs_all(context)

            # 3.6 播放视频（返回播放页）
            play_page = click_play_and_hold(detail_page)
            dismiss_dialogs_all(context)

            # 3.7 等待视频播放完成
            print("\n开始观看课程视频...")
            finished = wait_video_finish(play_page)
            if not finished:
                print("视频播放超时，跳过本课")

            # 3.8 关闭播放页/详情页，回到课程列表
            for pp in list(context.pages):
                if pp != page and "about:blank" not in pp.url:
                    try:
                        pp.close()
                    except Exception:
                        pass
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
        if context:
            context.close()
            print("浏览器已关闭。")


if __name__ == "__main__":
    main()
