"""页面操作模块 — 封装所有页面交互"""

import random
from playwright.sync_api import Page, BrowserContext

from config import (
    TIMEOUT,
    COURSE_CATEGORY_LABEL,
    QUERY_BUTTON_TEXT,
    LEARN_NOW_TEXT,
)


# === 学时数据读取 ===

def read_credit_data(page: Page) -> dict:
    """从学时管理系统首页(#/backIndex)读取学时数据。

    返回:
        {
            "requirements": {"专业课程": 60.0, "行业公需": 30.0, "一般公需": 30.0},
            "completed": {"专业课程": 148.0, "行业公需": 30.0, "一般公需": 0.0},
        }
    """
    print("读取学时数据...")

    # 定位「年度学时要求」和「现已完成学时」两个板块
    # 页面结构：.name1 是板块标题，.name2 内的 .Text 是数据行
    all_boxes = page.locator(".imgBox")
    requirements = {}
    completed = {}

    for i in range(all_boxes.count()):
        box = all_boxes.nth(i)
        title = box.locator(".name1").first.inner_text().strip()
        texts = box.locator(".name2 .Text")
        data = {}
        for j in range(texts.count()):
            line = texts.nth(j).inner_text().strip()
            # 格式如 "专业课程148.0学时" 或 "本年度需完成总学时90.0学时"
            data[j] = line
        if "年度学时要求" in title:
            requirements = _parse_credit_block(data)
        elif "现已完成学时" in title:
            completed = _parse_credit_block(data)

    print(f"  学时要求: {requirements}")
    print(f"  已完成: {completed}")
    return {"requirements": requirements, "completed": completed}


def _parse_credit_block(data: dict) -> dict:
    """解析学时板块文本为 {类别: 学时}。"""
    result = {}
    for line in data.values():
        for cat in ["专业课程", "行业公需", "一般公需"]:
            if cat in line:
                # 提取数字
                import re
                nums = re.findall(r"[\d.]+", line)
                if nums:
                    result[cat] = float(nums[-1])
    return result


def choose_category_to_study(credit_data: dict) -> str:
    """根据学时缺口选择要学习的课程类别。

    规则：优先选缺口最大的类别。所有类别都达标则返回 None。

    注意：页面「年度学时要求」只显示合并要求（行业公需+一般公需合计），
    但实际按 CREDIT_REQUIREMENTS 配置的 60/30/30 判断缺口。
    """
    from config import CREDIT_REQUIREMENTS

    completed = credit_data.get("completed", {})

    gaps = {}
    for cat in CREDIT_REQUIREMENTS:
        need = CREDIT_REQUIREMENTS[cat]
        done = completed.get(cat, 0)
        gap = need - done
        if gap > 0:
            gaps[cat] = gap

    if not gaps:
        print("所有类别学时均已达标！")
        return None

    # 选缺口最大的
    chosen = max(gaps, key=gaps.get)
    print(f"学时缺口: {gaps}，选择学习「{chosen}」（缺 {gaps[chosen]} 学时）")
    return chosen


# === 课程类别下拉框 ===

def click_dropdown(page: Page) -> None:
    """点击"课程类别"下拉框，展开选项列表。"""
    print(f"正在点击「{COURSE_CATEGORY_LABEL}」下拉框...")

    # 页面结构: .selectList 容器内有多个 el-select，第一个就是课程类别
    select_list = page.locator(".selectList").first
    dropdown = select_list.locator(".el-select").first.locator(".el-select__wrapper")
    if dropdown.count() > 0:
        dropdown.click()
        page.wait_for_timeout(600)
        print("下拉框已展开")
        return

    raise Exception("无法找到「课程类别」下拉框")


def select_option(page: Page, option_text: str) -> None:
    """在可见的下拉列表中选中指定选项。"""
    print(f"正在选择选项「{option_text}」...")
    page.wait_for_timeout(300)

    # 在可见的 popper 中找选项
    option = page.locator(f".el-select__popper:visible .el-select-dropdown__item:has-text('{option_text}')")
    if option.count() > 0:
        option.first.click(force=True)
        page.wait_for_timeout(500)
        print(f"已选择「{option_text}」")
        return

    raise Exception(f"未找到选项「{option_text}」")


def select_course_category(page: Page, category: str) -> None:
    """展开课程类别下拉框并选择指定类别。"""
    click_dropdown(page)
    select_option(page, category)


# === 查询按钮 ===

def click_query(page: Page) -> None:
    """点击「查询」按钮。"""
    print(f"正在点击「{QUERY_BUTTON_TEXT}」按钮...")
    button = page.locator(f"button:has-text('{QUERY_BUTTON_TEXT}')").first
    button.click()
    page.wait_for_timeout(2000)
    print("已点击查询按钮，等待结果加载...")


# === 课程列表 ===

def get_course_items(page: Page) -> list:
    """获取当前页面中的课程卡片列表。先确保在正确的页面。"""
    print("等待课程数据加载...")
    page.wait_for_timeout(2000)

    title = page.title()
    url = page.url
    print(f"  当前页面: url={url[:100]}, title={title}")

    items = page.locator(".itemBox")
    count = items.count()
    if count > 0:
        print(f"找到 {count} 门课程")
        return items.all()

    pagination = page.locator(".el-pagination")
    if pagination.count() > 0:
        print("检测到分页组件但无itemBox，可能是查询结果为空或仍在加载...")
        page.wait_for_timeout(5000)
        items = page.locator(".itemBox")
        count = items.count()
        if count > 0:
            print(f"延迟加载后找到 {count} 门课程")
            return items.all()

    print("未找到课程列表")
    return []


def parse_duration(item) -> int:
    """解析课程卡片中的时长（分钟）。

    itemBox 内 .Line2 行有「时长：XX 分钟」。解析失败返回 9999（视为最长）。
    """
    try:
        texts = item.locator(".Line2-item").all_inner_texts()
        for t in texts:
            if "时长" in t:
                # 提取数字分钟
                import re
                nums = re.findall(r"[\d.]+", t)
                if nums:
                    return int(float(nums[0]))
    except Exception:
        pass
    return 9999


def shortest_course(items: list):
    """从课程卡片列表中选择时长最短的一门。"""
    best = None
    best_dur = 9999
    for item in items:
        dur = parse_duration(item)
        if dur < best_dur:
            best_dur = dur
            best = item
    if best is not None:
        try:
            name = best.locator(".Line span").first.inner_text()
        except Exception:
            name = "(未知)"
        print(f"选择时长最短课程: {name}（{best_dur} 分钟）")
    return best


def enter_course_by_item(page: Page, context: BrowserContext, item) -> Page:
    """点击指定课程卡片进入详情页（新标签页）。"""
    with context.expect_page(timeout=TIMEOUT) as new_page_info:
        item.locator("img").first.click()
    detail_page = new_page_info.value
    detail_page.bring_to_front()
    print(f"已打开课程详情: {detail_page.url}")
    _wait_page_ready(detail_page)
    return detail_page


def random_enter_course(page: Page, context: BrowserContext) -> Page:
    """随机选择一门课程进入详情页。"""
    items = get_course_items(page)
    if not items:
        raise Exception("课程列表为空，无法选择课程")

    chosen = random.choice(items)
    course_name = chosen.locator(".Line span").first.inner_text() or "(未能读取)"
    print(f"随机选择了课程: {course_name}")

    return enter_course_by_item(page, context, chosen)


def shortest_enter_course(page: Page, context: BrowserContext) -> Page:
    """选择时长最短的课程进入详情页。"""
    items = get_course_items(page)
    if not items:
        raise Exception("课程列表为空，无法选择课程")

    chosen = shortest_course(items)
    return enter_course_by_item(page, context, chosen)


def _wait_page_ready(page: Page) -> None:
    """等待页面加载完成。"""
    try:
        page.wait_for_load_state("networkidle", timeout=TIMEOUT)
    except Exception:
        page.wait_for_timeout(3000)
    print(f"页面就绪: {page.title()}")


# === 立即学习 ===

def click_learn_now(page: Page) -> None:
    """在课程详情页等待并点击「立即学习」按钮。按钮可能需要几秒才出现。"""
    print("正在等待「立即学习」按钮出现...")

    # 等按钮出现，最多等 30 秒
    try:
        page.wait_for_selector("button:has-text('立即学习')", timeout=30000)
        page.wait_for_timeout(500)
        page.locator("button:has-text('立即学习')").first.click()
        print("已点击「立即学习」")
        page.wait_for_timeout(2000)
        return
    except Exception:
        pass

    # 兜底：遍历
    for i in range(page.locator("button").count()):
        t = "".join(page.locator("button").nth(i).all_inner_texts()).strip()
        if "立即学习" in t:
            page.locator("button").nth(i).click()
            print(f"已点击「立即学习」(按钮[{i}])")
            page.wait_for_timeout(2000)
            return

    print("未找到「立即学习」按钮")
    page.screenshot(path="debug_no_learn_button.png", full_page=True)


def click_play_and_hold(page: Page):
    """在视频播放页面找到「Play Video」按钮并点击，返回播放页。

    点击「立即学习」后可能开了新标签页(#/class)，播放按钮在播放页上。
    """
    print("正在等待播放页面加载...")
    page.wait_for_timeout(3000)

    print("正在查找「Play Video」按钮...")

    # 先找播放页（URL 含 /class 的标签页）
    context = page.context
    play_page = None
    for p in context.pages:
        if "/class" in p.url:
            play_page = p
            break
    if play_page is None:
        play_page = page

    # 在播放页尝试点击 Play Video
    found = _try_click_play_video(play_page)
    if found:
        return play_page

    # 兜底：检查 iframe
    frames = play_page.frames
    for f in frames:
        if _try_click_play_video(f):
            return play_page

    print("未找到 Play Video 按钮")
    play_page.screenshot(path="debug_no_play.png", full_page=True)
    return play_page


def _try_click_play_video(target) -> bool:
    """在 target（Page 或 Frame）中尝试点击 Play Video 按钮。"""
    btn = target.locator("button:has-text('Play Video')")
    if btn.count() > 0:
        btn.first.click()
        target.wait_for_timeout(3000)
        print("已点击 Play Video")
        target.screenshot(path="playing.png")
        print("截图已保存: playing.png")
        return True

    # 也尝试直接在 video 元素上点击
    video = target.locator("video")
    if video.count() > 0:
        video.first.click()
        target.wait_for_timeout(3000)
        print("已点击 video 元素")
        target.screenshot(path="playing.png")
        return True

    return False


# === 播放完成检测 ===

def wait_video_finish(page: Page, timeout_sec: int = 7200) -> bool:
    """等待视频播放完成。

    在播放页注入 JS 监听 video 的 ended 事件，轮询直到播放完。

    返回:
        True 表示播放完成，False 表示超时
    """
    print("开始监听视频播放进度...")

    # 注入监听器
    page.evaluate("""
        window.__video_progress = {ended: false, current: 0, duration: 0};
        const v = document.querySelector('video');
        if (v) {
            window.__video_progress.duration = v.duration || 0;
            v.addEventListener('timeupdate', () => {
                window.__video_progress.current = v.currentTime;
            });
            v.addEventListener('ended', () => {
                window.__video_progress.ended = true;
            });
        }
    """)

    waited = 0
    last_print = 0
    while waited < timeout_sec:
        page.wait_for_timeout(30000)  # 每 30 秒检查一次
        waited += 30

        try:
            progress = page.evaluate("window.__video_progress")
        except Exception:
            # 页面可能跳转了
            print(f"  页面状态异常，可能已跳转")
            return True

        if progress.get("ended"):
            print(f"  视频播放完成！({waited}s)")
            return True

        # 每 5 分钟打印一次进度
        if waited - last_print >= 300:
            last_print = waited
            current = progress.get("current", 0)
            duration = progress.get("duration", 0)
            pct = (current / duration * 100) if duration else 0
            print(f"  播放进度: {current:.0f}/{duration:.0f}s ({pct:.0f}%)")

    print(f"  等待视频播放超时 ({timeout_sec}s)")
    return False


def is_video_finished(page: Page) -> bool:
    """检查视频是否已播放完成（ended 状态）。"""
    try:
        return bool(page.evaluate("window.__video_progress ? window.__video_progress.ended : false"))
    except Exception:
        return False


# === 弹框处理 ===

def _check_page_dialogs(pg) -> bool:
    """检查单个页面，有弹框就点确定。返回 True 表示处理了弹框。"""
    try:
        dlg = pg.locator(".el-message-box:visible")
        if dlg.count() > 0:
            btn = dlg.locator("button:has-text('确定')")
            if btn.count() == 0:
                btn = dlg.locator("button:has-text('确认')")
            if btn.count() > 0:
                btn.first.click()
                print(f"已关闭 MessageBox 弹框: 确定")
                return True

        overlay = pg.locator(".el-overlay:visible button:has-text('确定')")
        if overlay.count() > 0:
            overlay.first.click()
            print("已关闭 overlay 弹框")
            return True

        dlg2 = pg.locator("dialog[open] button:has-text('确定'), dialog[open] button:has-text('确认')")
        if dlg2.count() > 0:
            dlg2.first.click()
            print("已关闭 HTML dialog 弹框")
            return True
    except Exception:
        pass
    return False


def dismiss_dialogs_all(context) -> None:
    """同步遍历所有标签页，有弹框就点确定。"""
    for pg in context.pages:
        if "about:blank" not in pg.url:
            _check_page_dialogs(pg)
