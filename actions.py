"""页面操作模块 — 封装所有页面交互"""

import random
import re
from decimal import Decimal, InvalidOperation
from playwright.sync_api import Page, BrowserContext

from config import (
    TIMEOUT,
    COURSE_CATEGORY_LABEL,
    QUERY_BUTTON_TEXT,
    LEARN_NOW_TEXT,
    MAX_PAGE_NAVIGATION_STEPS,
    SAVE_PLAYBACK_SCREENSHOTS,
    COURSE_PAGE_START,
    COURSE_PAGE_END,
)


class CourseCatalogEntryNotFoundError(RuntimeError):
    """保存的课程目录项已经不在当前前五页中。"""


# === 学时数据读取 ===

def read_credit_data(page: Page, allow_refresh: bool = True) -> dict:
    """从学时管理系统首页(#/backIndex)读取学时数据。

    返回:
        {
            "requirements": {"专业课程": 60.0, "行业公需": 30.0, "一般公需": 30.0},
            "completed": {"专业课程": 148.0, "行业公需": 30.0, "一般公需": 0.0},
        }
    """
    print("读取学时数据...")

    if page.locator(".imgBox").count() == 0:
        raise RuntimeError("当前页面不是学时管理系统，未找到学时面板")
    try:
        page.wait_for_selector(".imgBox .name1", timeout=10_000)
    except Exception:
        pass

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

    from config import CREDIT_REQUIREMENTS
    missing = [cat for cat in CREDIT_REQUIREMENTS if cat not in completed]
    if missing:
        if allow_refresh:
            print(
                f"学时类别尚未完整渲染（缺少: {', '.join(missing)}），刷新学时页面后重试..."
            )
            try:
                page.reload(wait_until="domcontentloaded", timeout=TIMEOUT)
                page.wait_for_selector(".imgBox .name1", timeout=15_000)
            except Exception as exc:
                print(f"刷新学时页面失败: {exc}")
            return read_credit_data(page, allow_refresh=False)
        raise RuntimeError(f"学时页面缺少独立类别数据: {', '.join(missing)}")

    print(f"  学时要求: {requirements}")
    print(f"  已完成: {completed}")
    return {"requirements": requirements, "completed": completed}


def _parse_credit_block(data: dict) -> dict:
    """解析学时板块文本为 {类别: 学时}。"""
    result = {}
    for line in data.values():
        # 页面会把行业公需和一般公需的年度要求合并展示，不能归入任一单独类别。
        if "行业公需和一般公需" in line:
            continue
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
    missing = [cat for cat in CREDIT_REQUIREMENTS if cat not in completed]
    if missing:
        raise RuntimeError(f"缺少类别学时，无法计算缺口: {', '.join(missing)}")

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
    try:
        page.wait_for_selector(".selectList .el-select", timeout=10_000)
    except Exception:
        pass
    select_list = page.locator(".selectList").first
    dropdown = select_list.locator(".el-select").first.locator(".el-select__wrapper")
    if dropdown.count() > 0:
        dropdown.click()
        try:
            page.wait_for_selector(
                ".el-select__popper:visible .el-select-dropdown__item",
                timeout=5_000,
            )
        except Exception:
            page.wait_for_timeout(300)
        print("下拉框已展开")
        return

    raise Exception("无法找到「课程类别」下拉框")


def select_option(page: Page, option_text: str) -> None:
    """在可见的下拉列表中选中指定选项。"""
    print(f"正在选择选项「{option_text}」...")
    # 在可见的 popper 中找选项
    option = page.locator(f".el-select__popper:visible .el-select-dropdown__item:has-text('{option_text}')")
    try:
        option.first.wait_for(state="visible", timeout=10_000)
    except Exception:
        pass
    if option.count() > 0:
        option.first.click(force=True)
        page.wait_for_timeout(500)
        print(f"已选择「{option_text}」")
        return

    raise Exception(f"未找到选项「{option_text}」")


def select_course_category(page: Page, category: str, allow_reload: bool = True) -> None:
    """展开课程类别下拉框并选择指定类别。"""
    try:
        click_dropdown(page)
        select_option(page, category)
    except Exception:
        if not allow_reload:
            raise
        print(f"课程类别「{category}」尚未加载，刷新课程页后重试...")
        page.reload(wait_until="domcontentloaded", timeout=TIMEOUT)
        page.wait_for_selector(".selectList", timeout=15_000)
        select_course_category(page, category, allow_reload=False)


# === 查询按钮 ===

def click_query(page: Page) -> None:
    """点击「查询」按钮。"""
    print(f"正在点击「{QUERY_BUTTON_TEXT}」按钮...")
    button = page.locator(f"button:has-text('{QUERY_BUTTON_TEXT}')").first
    button.click()
    try:
        page.wait_for_selector(".itemBox, .el-pagination", timeout=TIMEOUT)
    except Exception:
        page.wait_for_timeout(500)
    print("已点击查询按钮，等待结果加载...")


# === 课程列表 ===

def get_course_items(page: Page) -> list:
    """获取当前页面中的课程卡片列表。先确保在正确的页面。"""
    print("等待课程数据加载...")
    try:
        page.wait_for_selector(".itemBox", timeout=10_000)
    except Exception:
        pass

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
        try:
            page.wait_for_selector(".itemBox", timeout=5_000)
        except Exception:
            pass
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


def parse_numeric_field(value, labels=()) -> float | None:
    """Parse a decimal value from visible text, returning None for unknown data."""
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    if labels:
        if not any(label in text for label in labels):
            return None
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(Decimal(match.group(0)))
    except (InvalidOperation, ValueError):
        return None


def parse_credit_hours(value) -> float | None:
    """Parse an explicit credit-hour value; unknown is never treated as zero."""
    return parse_numeric_field(value, ("学时", "学分", "credit", "hour"))


def normalize_course_record(record: dict, category: str | None = None) -> dict:
    """Normalize new and legacy catalog records without inventing credit values."""
    normalized = dict(record or {})
    duration = normalized.get("duration_minutes", normalized.get("duration"))
    try:
        duration = int(float(duration)) if duration is not None else 9999
    except (TypeError, ValueError):
        duration = 9999
    normalized["duration_minutes"] = duration
    normalized.setdefault("duration", duration)
    credit = normalized.get("credit_hours")
    if credit is not None:
        credit = parse_credit_hours(str(credit)) if isinstance(credit, str) else parse_numeric_field(credit)
    normalized["credit_hours"] = credit
    normalized["credit_source"] = normalized.get("credit_source", "unknown")
    if category and not normalized.get("category"):
        normalized["category"] = category
    return normalized


def course_record_from_item(item, category: str | None = None, position: int | None = None) -> dict:
    """Snapshot card metadata once, including explicit credit hours when present."""
    title = _course_title(item)
    texts = []
    for selector in (".Line", ".Line2-item", ".credit", ".hours", "[class*=credit]", "[class*=hour]"):
        try:
            texts.extend(item.locator(selector).all_inner_texts())
        except Exception:
            continue
    credit = next((parse_credit_hours(text) for text in texts if parse_credit_hours(text) is not None), None)
    duration = parse_duration(item)
    record = {
        "key": course_key(item),
        "title": title,
        "duration_minutes": duration,
        "duration": duration,
        "credit_hours": credit,
        "credit_source": "card" if credit is not None else "unknown",
    }
    if category:
        record["category"] = category
    if position is not None:
        record["position"] = position
    return record


def select_course_combination(records: list[dict], gap: float, max_candidates: int = 80):
    """Return a minimum-duration combination covering gap using bounded DP."""
    # Catalogs may be loaded from an older scan whose order reflects page order.
    # Rank before applying the bound so short, high-credit courses are never
    # omitted merely because they appeared later in the catalog.
    normalized_records = [normalize_course_record(record) for record in records]
    normalized_records.sort(
        key=lambda item: (
            -((item.get("credit_hours") or 0) / max(item.get("duration_minutes", 9999), 1)),
            item.get("duration_minutes", 9999),
            item.get("page", 0),
            item.get("position", 0),
        )
    )
    candidates = []
    for item in normalized_records[:max_candidates]:
        credit = item.get("credit_hours")
        duration = item.get("duration_minutes", 9999)
        if credit is None or credit <= 0 or duration >= 9999:
            continue
        candidates.append(item)
    if gap <= 0 or not candidates:
        return []
    scale = 2
    target = int(round(gap * scale))
    states = {0: (0, 0, 0.0, ())}
    for index, item in enumerate(candidates):
        value = max(1, int(round(item["credit_hours"] * scale)))
        duration = item["duration_minutes"]
        for covered, (total, count, _old_efficiency, path) in list(states.items()):
            new_covered = min(target, covered + value)
            efficiency = sum(
                candidates[item_index].get("credit_hours", 0) / max(candidates[item_index].get("duration_minutes", 1), 1)
                for item_index in path
            ) + item.get("credit_hours", 0) / max(duration, 1)
            candidate = (total + duration, count + 1, -efficiency, path + (index,))
            old = states.get(new_covered)
            if old is None or candidate[:3] < old[:3]:
                states[new_covered] = candidate
    if target not in states:
        return []
    path = states[target][3]
    return [candidates[index] for index in path]


def filter_credit_candidates(records, learned=None, failed=None, category=None):
    learned = learned or set()
    failed = failed or set()
    result = []
    for record in records:
        item = normalize_course_record(record, category)
        if item.get("key") in learned or item.get("key") in failed:
            continue
        if category and item.get("category") not in (None, category):
            continue
        if item.get("duration_minutes", 9999) < 9999:
            result.append(item)
    return result


def rank_by_credit_efficiency(records):
    """Rank fallback candidates by credit hours per playback minute."""
    return sorted(
        records,
        key=lambda item: (
            -((item.get("credit_hours") or 0) / max(item.get("duration_minutes", item.get("duration", 9999)), 1)),
            item.get("duration_minutes", item.get("duration", 9999)),
            item.get("page", 0),
            item.get("position", 0),
        ),
    )


def course_key(item) -> str:
    """读取课程稳定标识，优先使用课程链接中的 courseid。"""
    try:
        for selector in ("a", "img"):
            locator = item.locator(selector).first
            if locator.count() == 0:
                continue
            for attr in ("href", "data-course-id"):
                value = locator.get_attribute(attr)
                if value:
                    match = re.search(r"courseid[=/]([A-Za-z0-9_-]+)", value, re.I)
                    if match:
                        return match.group(1)
                    # href="#"、javascript: 等不是课程标识，不能用于去重。
                    if attr == "href" and value.strip().lower() not in {
                        "#", "javascript:void(0)", "javascript:;"
                    }:
                        return value
    except Exception:
        pass
    try:
        title = item.locator(".Line span").first.inner_text().strip()
    except Exception:
        title = "unknown"
    return f"title:{title}|duration:{parse_duration(item)}"


def course_key_from_url(url: str) -> str:
    match = re.search(r"courseid[=/]([A-Za-z0-9_-]+)", url or "", re.I)
    return match.group(1) if match else url


def _course_candidate_records(items: list, excluded: set[str] | None = None) -> list[dict]:
    """一次读取课程卡片所需字段，后续排序不再反复访问浏览器 DOM。"""
    excluded = excluded or set()
    records = []
    for item in items:
        key = course_key(item)
        if key in excluded:
            continue
        duration = parse_duration(item)
        try:
            title = item.locator(".Line span").first.inner_text().strip()
        except Exception:
            title = "(未知)"
        records.append({"item": item, "key": key, "title": title, "duration": duration})
    return records


def _course_title(item) -> str:
    try:
        return item.locator(".Line span").first.inner_text().strip()
    except Exception:
        return ""


def collect_course_catalog(
    page: Page,
    max_pages: int = 5,
    category: str | None = None,
) -> list[dict]:
    """首次扫描课程前五页，保存课程位置和时长，后续直接使用该目录。"""
    max_pages = max(1, max_pages)
    try:
        _goto_course_page_number(page, 1)
    except Exception as exc:
        print(f"无法回到课程第 1 页，将使用当前页开始扫描: {exc}")

    catalog = []
    for page_number in range(1, max_pages + 1):
        items = get_course_items(page)
        for position, item in enumerate(items):
            record = course_record_from_item(item, category, position)
            if record["duration_minutes"] >= 9999:
                continue
            record["page"] = page_number
            catalog.append(record)
        print(f"已记录课程目录第 {page_number} 页，共 {len(items)} 门")
        if page_number >= max_pages:
            break
        old_items = page.locator(".itemBox").all()
        if not _goto_next_course_page(page, old_items):
            print(f"课程在第 {page_number} 页结束，共扫描 {page_number} 页")
            break

    catalog.sort(key=lambda item: (item["duration"], item["page"], item["position"]))
    print(f"首次课程目录建立完成，共记录 {len(catalog)} 门课程")
    return catalog


def enter_catalog_course(
    page: Page,
    context: BrowserContext,
    record: dict,
    excluded: set[str] | None = None,
) -> Page:
    """按已保存的页码、位置和课程标识进入队列中的下一门课程。"""
    excluded = excluded or set()
    if record.get("key") in excluded:
        raise RuntimeError(f"课程已被排除: {record.get('title', '(未知)')}")

    original_record = record
    record = normalize_course_record(record)
    _goto_course_page_number(page, int(record["page"]))
    items = get_course_items(page)
    chosen = None
    for item in items:
        if course_key(item) == record.get("key"):
            chosen = item
            break
    if chosen is None:
        for item in items:
            if (
                _course_title(item) == record.get("title")
                and parse_duration(item) == record.get("duration_minutes", record.get("duration"))
            ):
                chosen = item
                break
    if chosen is None:
        position = int(record.get("position", -1))
        if 0 <= position < len(items):
            candidate = items[position]
            if parse_duration(candidate) == record.get("duration_minutes", record.get("duration")):
                chosen = candidate
    if chosen is None:
        print(
            f"课程目录位置已变化，开始在第 1 至第 {COURSE_PAGE_END} 页修复: "
            f"{record.get('title', '(未知)')}"
        )
        chosen = _repair_catalog_course_location(page, record)
    if chosen is None:
        raise CourseCatalogEntryNotFoundError(
            f"课程目录中的课程在第 1 至第 {COURSE_PAGE_END} 页均无法定位: "
            f"{record.get('title', '(未知)')}"
        )
    detail_page = enter_course_by_item(page, context, chosen)
    detail_meta = extract_detail_course_metadata(detail_page)
    if detail_meta.get("credit_hours") is not None:
        old_credit = record.get("credit_hours")
        if old_credit is not None and abs(old_credit - detail_meta["credit_hours"]) > 0.001:
            print(f"课程学时字段冲突，采用详情页值: {old_credit} -> {detail_meta['credit_hours']}")
        record.update(detail_meta)
        record["credit_source"] = "detail"
        original_record.update(detail_meta)
        original_record["credit_source"] = "detail"
    return detail_page


def extract_detail_course_metadata(page: Page) -> dict:
    """Read explicit duration/credit text from a course detail page."""
    try:
        text = page.locator("body").inner_text()
    except Exception:
        return {}
    credit = None
    for line in text.splitlines():
        if credit is None:
            credit = parse_credit_hours(line)
    duration = parse_numeric_field(text, ("时长", "分钟", "duration"))
    result = {}
    if credit is not None:
        result["credit_hours"] = credit
    if duration is not None:
        result["duration_minutes"] = int(duration)
        result["duration"] = int(duration)
    return result


def _repair_catalog_course_location(page: Page, record: dict):
    """仅在保存位置失效时重新扫描前五页，并更新该目录项的位置。"""
    try:
        _goto_course_page_number(page, 1)
    except Exception:
        pass

    for page_number in range(1, COURSE_PAGE_END + 1):
        items = get_course_items(page)
        for position, item in enumerate(items):
            same_key = course_key(item) == record.get("key")
            same_description = (
                _course_title(item) == record.get("title")
                and parse_duration(item) == record.get("duration")
            )
            if same_key or same_description:
                record.update(
                    {
                        "key": course_key(item),
                        "page": page_number,
                        "position": position,
                    }
                )
                print(f"已修复课程位置: 第 {page_number} 页第 {position + 1} 门")
                return item
        if page_number < COURSE_PAGE_END:
            old_items = page.locator(".itemBox").all()
            if not _goto_next_course_page(page, old_items):
                break
    return None


def shortest_course(items: list, excluded: set[str] | None = None):
    """从课程卡片列表中选择时长最短的一门。"""
    excluded = excluded or set()
    best = None
    best_dur = 9999
    eligible_count = 0
    for item in items:
        if course_key(item) in excluded:
            continue
        eligible_count += 1
        dur = parse_duration(item)
        if dur < best_dur:
            best_dur = dur
            best = item
    if eligible_count and best is None:
        raise RuntimeError("课程列表中没有包含有效时长的课程")
    if best is not None:
        try:
            name = best.locator(".Line span").first.inner_text()
        except Exception:
            name = "(未知)"
        print(f"选择时长最短课程: {name}（{best_dur} 分钟）")
    return best


def enter_course_by_item(page: Page, context: BrowserContext, item) -> Page:
    """点击课程卡片，兼容新标签页和当前页跳转两种页面行为。"""
    old_url = page.url
    old_pages = set(context.pages)
    # 实际课程页没有 <a>；Vue 的跳转事件绑定在 .itemBox 卡片根节点。
    click_target = item

    try:
        click_target.scroll_into_view_if_needed()
        with context.expect_page(timeout=5000) as new_page_info:
            click_target.click()
        detail_page = new_page_info.value
    except Exception:
        page.wait_for_timeout(1500)
        new_pages = [p for p in context.pages if p not in old_pages]
        if new_pages:
            detail_page = new_pages[0]
        elif page.url != old_url or page.locator("button:has-text('立即学习')").count() > 0:
            detail_page = page
        else:
            # 有些页面的链接 href 是占位符，真正的点击事件绑定在图片上。
            image_target = item.locator("img").first
            if image_target.count() > 0:
                try:
                    with context.expect_page(timeout=5000) as new_page_info:
                        image_target.click()
                    detail_page = new_page_info.value
                except Exception:
                    page.wait_for_timeout(1500)
                    new_pages = [p for p in context.pages if p not in old_pages]
                    if new_pages:
                        detail_page = new_pages[0]
                    elif page.url != old_url or page.locator("button:has-text('立即学习')").count() > 0:
                        detail_page = page
                    else:
                        raise RuntimeError("课程链接和图片点击后都没有跳转")
            elif page.url != old_url or page.locator("button:has-text('立即学习')").count() > 0:
                detail_page = page
            else:
                raise RuntimeError("课程卡片点击后页面没有跳转，请检查课程链接或页面状态")

    detail_page.bring_to_front()
    print(f"已打开课程详情: {detail_page.url}")
    _wait_page_ready(detail_page)
    item_key = course_key(item)
    detail_page._course_key = (
        course_key_from_url(detail_page.url)
        if re.search(r"courseid[=/][A-Za-z0-9_-]+", detail_page.url or "", re.I)
        else item_key
    )
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


def shortest_enter_course(
    page: Page, context: BrowserContext, excluded: set[str] | None = None
) -> Page:
    """从当前页开始选择最短未学习课程，当前页耗尽时自动翻页。"""
    excluded = excluded or set()
    for page_number in range(1, 101):
        items = get_course_items(page)
        if not items:
            raise RuntimeError(f"第 {page_number} 页没有课程，无法选择课程")

        chosen = shortest_course(items, excluded)
        if chosen is not None:
            return enter_course_by_item(page, context, chosen)

        print(f"第 {page_number} 页的 {len(items)} 门课程都已学习，尝试下一页...")
        if not _goto_next_course_page(page, items):
            raise RuntimeError("课程列表已翻完，没有找到未学习课程")

    raise RuntimeError("翻页超过 100 页，停止寻找课程")


def _goto_next_course_page(page: Page, old_items: list) -> bool:
    """点击课程分页下一页；下一页不存在或按钮禁用时返回 False。"""
    next_button = page.locator(".el-pagination .btn-next:visible")
    if next_button.count() == 0:
        return False
    try:
        if not next_button.first.is_enabled():
            return False
        old_keys = {course_key(item) for item in old_items}
        next_button.first.click()
        for _ in range(20):
            page.wait_for_timeout(500)
            new_items = page.locator(".itemBox").all()
            if new_items and {course_key(item) for item in new_items} != old_keys:
                print(f"已切换到下一页，找到 {len(new_items)} 门课程")
                return True
    except Exception as exc:
        print(f"切换课程下一页失败: {exc}")
    return False


def _course_page_count(page: Page, item_count: int) -> int:
    """根据分页总数和当前页数量估算课程总页数。"""
    pagination = page.locator(".el-pagination")
    if pagination.count() == 0 or item_count <= 0:
        return 1
    text = pagination.first.inner_text()
    match = re.search(r"共\s*(\d+)\s*条", text)
    return max(1, (int(match.group(1)) + item_count - 1) // item_count) if match else 1


def _current_course_page_number(page: Page) -> int:
    active = page.locator(
        ".el-pagination li.number[aria-current='true'], "
        ".el-pagination li.number.is-active, "
        ".el-pagination li.number.active"
    )
    if active.count() > 0:
        match = re.search(r"\d+", active.first.inner_text())
        if match:
            return int(match.group())
    return 1


def _visible_course_page_locator(page: Page, target: int):
    numbers = page.locator(".el-pagination li.number:visible")
    for index in range(numbers.count()):
        candidate = numbers.nth(index)
        try:
            if candidate.inner_text().strip() == str(target):
                return candidate
        except Exception:
            continue
    return None


def _goto_course_page_number(page: Page, target: int) -> None:
    """通过分页控件前进到指定页。"""
    current = _current_course_page_number(page)
    if target == current:
        return

    direct_target = _visible_course_page_locator(page, target)
    if direct_target is not None:
        old_items = page.locator(".itemBox").all()
        direct_target.click()
        for _ in range(20):
            page.wait_for_timeout(250)
            new_items = page.locator(".itemBox").all()
            if new_items and {
                course_key(item) for item in new_items
            } != {course_key(item) for item in old_items}:
                return
            # 活动页标记可能先更新，继续等待课程卡片完成 Vue 重渲染。
            if _current_course_page_number(page) == target and _ == 19:
                return
        print(f"点击课程第 {target} 页后未观察到数据变化，降级读取当前课程页")
        return

    steps = 0
    if target < current:
        first = _visible_course_page_locator(page, 1)
        if first is not None:
            first.click()
            page.wait_for_timeout(300)
            current = _current_course_page_number(page)
        else:
            quick_prev = page.locator(".el-pagination .btn-quickprev:visible")
            while quick_prev.count() > 0 and steps < 30:
                steps += 1
                quick_prev.first.click()
                page.wait_for_timeout(300)
                first = _visible_course_page_locator(page, 1)
                if first is not None:
                    first.click()
                    page.wait_for_timeout(300)
                    current = 1
                    steps = 0
                    break
                quick_prev = page.locator(".el-pagination .btn-quickprev:visible")
            else:
                raise RuntimeError("无法返回课程第 1 页")

    while current < target:
        steps += 1
        if steps > MAX_PAGE_NAVIGATION_STEPS:
            raise RuntimeError(
                f"从课程第 {current} 页跳转到第 {target} 页超过 {MAX_PAGE_NAVIGATION_STEPS} 次操作限制"
            )
        visible_target = _visible_course_page_locator(page, target)
        if visible_target is not None:
            visible_target.click()
            page.wait_for_timeout(300)
            current = _current_course_page_number(page)
            continue
        quick_next = page.locator(".el-pagination .btn-quicknext:visible")
        if quick_next.count() > 0 and quick_next.first.is_enabled():
            quick_next.first.click()
            for _ in range(20):
                page.wait_for_timeout(250)
                new_current = _current_course_page_number(page)
                if new_current != current:
                    current = new_current
                    break
            else:
                raise RuntimeError("课程分页快速跳转后页码没有变化")
            continue
        old_items = page.locator(".itemBox").all()
        if not _goto_next_course_page(page, old_items):
            raise RuntimeError(f"无法跳转到课程第 {target} 页")
        # 部分 Element UI 版本更新课程卡片但不更新 aria-current，成功翻页
        # 时按普通下一页推进，避免把同一页误判为未变化而重复点击。
        detected = _current_course_page_number(page)
        current = detected if detected > current else current + 1


def _reachable_course_pages(page: Page) -> list[int]:
    """返回分页器当前可直接点击的页码，避免随机抽样触发远距离逐页跳转。"""
    numbers = page.locator(".el-pagination li.number:visible")
    reachable = set()
    for index in range(numbers.count()):
        try:
            match = re.search(r"\d+", numbers.nth(index).inner_text())
            if match:
                reachable.add(int(match.group()))
        except Exception:
            continue
    reachable.add(_current_course_page_number(page))
    return sorted(reachable)


def random_three_shortest_enter_course(
    page: Page,
    context: BrowserContext,
    excluded: set[str] | None = None,
    sample_pages: int = 3,
) -> Page:
    """随机抽取若干课程页，在抽样页中选择时长最短的未学习课程。"""
    excluded = excluded or set()
    first_items = get_course_items(page)
    if not first_items:
        raise RuntimeError("当前页没有课程，无法选择课程")
    total_pages = _course_page_count(page, len(first_items))
    total_search_pages = min(total_pages, COURSE_PAGE_END)
    current_page = _current_course_page_number(page)
    if current_page < COURSE_PAGE_START or current_page > total_search_pages:
        _goto_course_page_number(page, COURSE_PAGE_START)
        current_page = COURSE_PAGE_START

    search_pages = list(range(COURSE_PAGE_START, total_search_pages + 1))
    reachable_pages = [
        number for number in _reachable_course_pages(page) if number in search_pages
    ]
    # 第 1 页重置后，目标范围内的页码可通过普通分页逐页到达；抽样仍限制为 3 页。
    if len(reachable_pages) < min(sample_pages, len(search_pages)):
        reachable_pages = search_pages
    other_pages = [number for number in reachable_pages if number != current_page]
    selected_pages = [current_page]
    selected_pages.extend(
        random.sample(other_pages, min(max(0, sample_pages - 1), len(other_pages)))
    )
    selected_pages = sorted(set(selected_pages))
    page_count = len(selected_pages)
    if len(reachable_pages) < sample_pages:
        print(
            f"分页器当前仅暴露 {len(reachable_pages)} 个可直接到达页码，"
            f"本轮降级抽取 {page_count} 页"
        )
    print(f"本轮随机抽取课程页: {selected_pages}（共 {total_pages} 页）")

    best_page = None
    best_record = None
    for page_number in selected_pages:
        try:
            _goto_course_page_number(page, page_number)
        except RuntimeError as exc:
            print(f"第 {page_number} 页无法稳定到达，跳过该抽样页: {exc}")
            continue
        items = get_course_items(page)
        records = _course_candidate_records(items, excluded)
        records = [r for r in records if r["duration"] < 9999]
        if not records:
            print(f"第 {page_number} 页没有未学习课程，跳过")
            continue
        candidate = min(records, key=lambda record: record["duration"])
        if best_record is None or candidate["duration"] < best_record["duration"]:
            best_page = page_number
            best_record = candidate

    if best_page is None:
        raise RuntimeError("随机抽取的课程页都没有未学习课程")

    try:
        _goto_course_page_number(page, best_page)
    except RuntimeError as exc:
        print(f"无法返回最短课程所在页，降级使用当前页: {exc}")
    items = get_course_items(page)
    chosen = None
    for item in items:
        if course_key(item) == best_record["key"]:
            chosen = item
            break
        # 页面重新渲染后，Vue 卡片的临时链接标识可能变化；同页标题和时长
        # 仍然相同时，视为同一门候选课程。
        if (
            _course_title(item) == best_record["title"]
            and parse_duration(item) == best_record["duration"]
        ):
            chosen = item
            break
    if chosen is None:
        available = [
            record
            for record in _course_candidate_records(items, excluded)
            if record["duration"] < 9999
        ]
        if available:
            chosen = min(available, key=lambda record: record["duration"])["item"]
            print("目标候选标识发生变化，已回退选择目标页当前最短未学习课程")
        else:
            raise RuntimeError("目标课程页刷新后找不到可学习课程")
    print(
        f"从随机抽取页中选择第 {best_page} 页的最短课程: "
        f"{best_record['title']}（{best_record['duration']} 分钟）"
    )
    return enter_course_by_item(page, context, chosen)


def _wait_page_ready(page: Page) -> None:
    """等待页面加载完成。"""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
    except Exception:
        page.wait_for_timeout(500)
    print(f"页面就绪: {page.title()}")


# === 立即学习 ===

def click_learn_now(page: Page) -> bool:
    """在课程详情页等待并点击「立即学习」按钮。按钮可能需要几秒才出现。"""
    print("正在等待「立即学习」按钮出现...")

    # 等按钮出现，最多等 30 秒
    visible_selector = "button:has-text('立即学习'):visible"
    try:
        page.wait_for_selector(visible_selector, timeout=30000)
        page.wait_for_timeout(500)
        visible_buttons = page.locator(visible_selector)
        if visible_buttons.count() == 0:
            raise RuntimeError("未找到可见的立即学习按钮")
        visible_buttons.first.click()
        print("已点击「立即学习」")
        page.wait_for_timeout(2000)
        return True
    except Exception:
        pass

    # 兜底：遍历
    buttons = page.locator("button")
    for i in range(buttons.count()):
        candidate = buttons.nth(i)
        try:
            if not candidate.is_visible() or not candidate.is_enabled():
                continue
            t = candidate.inner_text().strip()
        except Exception:
            continue
        if "立即学习" in t:
            try:
                candidate.click()
                print(f"已点击「立即学习」(按钮[{i}])")
                page.wait_for_timeout(2000)
                return True
            except Exception:
                continue

    print("未找到「立即学习」按钮")
    page.screenshot(path="debug_no_learn_button.png", full_page=True)
    raise RuntimeError("未找到「立即学习」按钮，无法开始课程")


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

    # 新标签页不一定自动成为前台页，后台页面会被 Chromium 降低定时器和
    # 渲染频率，表现为视频卡顿或进度比现实时间慢。
    if hasattr(play_page, "bring_to_front"):
        play_page.bring_to_front()
    # 播放页可能残留上一门课程的完成提示，或异步出现普通提示框；
    # 播放开始前两类阻塞弹窗都可以安全关闭。
    _clear_play_blocking_dialogs(play_page)
    try:
        play_page.wait_for_selector(
            "button:has-text('Play Video'), video", timeout=10_000
        )
    except Exception:
        play_page.wait_for_timeout(500)

    # 在播放页尝试点击 Play Video
    found = _try_click_play_video(play_page)
    if found:
        if _find_video_target(play_page) is None:
            raise RuntimeError("已点击播放控件，但未找到 video 元素")
        if hasattr(play_page, "bring_to_front"):
            play_page.bring_to_front()
        return play_page

    # 兜底：检查 iframe
    frames = play_page.frames
    for f in frames:
        if _try_click_play_video(f):
            if _find_video_target(play_page) is None:
                raise RuntimeError("已点击播放控件，但未找到 video 元素")
            if hasattr(play_page, "bring_to_front"):
                play_page.bring_to_front()
            return play_page

    print("未找到 Play Video 按钮")
    play_page.screenshot(path="debug_no_play.png", full_page=True)
    raise RuntimeError("未找到 Play Video 按钮，无法开始播放")


def _find_video_target(page: Page):
    """返回包含 video 元素的页面或 frame。"""
    if page.locator("video").count() > 0:
        return page
    for frame in page.frames:
        if frame != page.main_frame and frame.locator("video").count() > 0:
            return frame
    return None


def _try_click_play_video(target) -> bool:
    """在 target（Page 或 Frame）中尝试点击 Play Video 按钮。"""
    btn = target.locator("button:has-text('Play Video')")
    if btn.count() > 0:
        try:
            btn.first.click(timeout=5_000)
        except Exception:
            # 弹窗可能刚好在定位后出现，先关闭普通提示再重试一次。
            _check_page_dialogs(target)
            _dismiss_normal_dialogs(target)
            btn.first.click(timeout=5_000)
        target.wait_for_timeout(500)
        print("已点击 Play Video")
        if SAVE_PLAYBACK_SCREENSHOTS and hasattr(target, "screenshot"):
            target.screenshot(path="playing.png")
            print("截图已保存: playing.png")
        return True

    # 也尝试直接在 video 元素上点击
    video = target.locator("video")
    if video.count() > 0:
        video.first.click()
        target.wait_for_timeout(500)
        print("已点击 video 元素")
        if SAVE_PLAYBACK_SCREENSHOTS and hasattr(target, "screenshot"):
            target.screenshot(path="playing.png")
        return True

    return False


def _clear_play_blocking_dialogs(play_page) -> None:
    """播放开始前清理会拦截播放按钮的残留弹窗。"""
    pages = list(getattr(getattr(play_page, "context", None), "pages", []))
    if play_page not in pages:
        pages.append(play_page)
    for candidate in pages:
        try:
            if "about:blank" in candidate.url:
                continue
            _check_page_dialogs(candidate)
            _dismiss_normal_dialogs(candidate)
        except Exception:
            continue


# === 播放完成检测 ===

def wait_video_finish(page: Page, timeout_sec: int = 7200) -> bool:
    """等待视频播放完成。

    在播放页注入 JS 监听 video 的 ended 事件，轮询直到播放完。

    返回:
        True 表示播放完成，False 表示超时
    """
    print("开始监听视频播放进度...")

    if hasattr(page, "bring_to_front"):
        page.bring_to_front()

    target = _find_video_target(page)
    if target is None:
        raise RuntimeError("播放页面没有 video 元素")

    target.wait_for_timeout(1000)
    state_script = """() => {
        const v = document.querySelector('video');
        if (!v) return null;
        return {
            paused: v.paused,
            ended: v.ended,
            current: v.currentTime || 0,
            duration: Number.isFinite(v.duration) ? v.duration : 0,
            playbackRate: v.playbackRate,
            readyState: v.readyState,
            error: v.error ? (v.error.message || `MediaError ${v.error.code}`) : null
        };
    }"""
    try:
        initial = target.evaluate(state_script)
    except Exception:
        print("播放页面在开始检查时已关闭或跳转")
        return False
    if not initial or initial.get("duration", 0) <= 0:
        raise RuntimeError("视频没有加载有效时长")
    if initial.get("paused") and initial.get("current", 0) <= 0:
        raise RuntimeError("视频未开始播放")
    if abs((initial.get("playbackRate") or 1) - 1) > 0.01:
        raise RuntimeError("视频不是正常 1 倍速播放")

    waited = 0
    last_print = 0
    poll_sec = 5
    last_current = initial.get("current", 0) or 0
    stalled_for = 0
    rate_window_elapsed = 0
    rate_window_advanced = 0.0
    slow_windows = 0
    while waited < timeout_sec:
        page.wait_for_timeout(min(poll_sec, timeout_sec - waited) * 1000)
        waited += min(poll_sec, timeout_sec - waited)

        try:
            if "zlb_login_bridge" in page.url:
                print("  会话已跳转到登录页面")
                return False
            progress = target.evaluate(state_script)
        except Exception:
            print("  播放页面状态异常或已关闭")
            return False

        if not progress:
            print("  video 元素已消失，页面可能被重新加载")
            return False
        if progress.get("error"):
            print(f"  视频播放错误: {progress['error']}")
            return False

        # 完成弹窗必须留给主流程处理，否则这里会先关闭弹窗，后续无法确认学分。
        if _has_completion_dialog(page.context):
            print("  检测到课程完成弹窗，交由主流程确认...")
            return True

        # 平台会定时弹出在线确认并暂停视频。确认后继续等待播放器恢复，
        # 不能把这次正常暂停当作课程失败。
        if _dismiss_playback_interruption_dialogs(page.context):
            print("  已确认在线学习，继续监控视频播放...")
            stalled_for = 0
            rate_window_elapsed = 0
            rate_window_advanced = 0.0
            slow_windows = 0
            last_current = progress.get("current", 0) or 0
            continue

        duration = progress.get("duration", 0) or 0
        current = progress.get("current", 0) or 0
        if progress.get("ended") and duration > 0 and current >= duration - 1.5:
            print(f"  视频播放完成！({waited}s)")
            return True

        if abs((progress.get("playbackRate") or 1) - 1) > 0.01:
            print("  检测到播放速度不再是 1 倍速")
            return False

        advanced = current - last_current
        if advanced >= 1:
            stalled_for = 0
        else:
            stalled_for += poll_sec
        last_current = current

        rate_window_elapsed += poll_sec
        rate_window_advanced += max(0, advanced)
        if rate_window_elapsed >= 30:
            effective_rate = rate_window_advanced / rate_window_elapsed
            if effective_rate < 0.75:
                slow_windows += 1
                print(
                    f"  播放进度偏慢: 近 {rate_window_elapsed} 秒只前进了 "
                    f"{rate_window_advanced:.1f} 秒（有效 {effective_rate:.2f} 倍速）"
                )
            else:
                slow_windows = 0
            rate_window_elapsed = 0
            rate_window_advanced = 0.0

        if slow_windows >= 2:
            print("  视频连续一分钟明显慢于正常速度，可能正在频繁缓冲")
            return False

        if progress.get("paused") and not progress.get("ended"):
            print(f"  视频已暂停在 {current:.0f}/{duration:.0f}s，请检查页面提示")
            return False
        if stalled_for >= 30 and progress.get("readyState", 0) >= 2:
            print(f"  视频进度已停滞 {stalled_for} 秒，请检查网络或页面提示")
            return False

        # 每 5 分钟打印一次进度
        if waited - last_print >= 300:
            last_print = waited
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

def _is_credit_completion_message(message: str) -> bool:
    """判断是否是已经获得学分的完成弹窗，而不是进入未完成课程的询问。"""
    return "获得学分" in message or "学习时间已达到要求" in message


def _is_resume_learning_message(message: str) -> bool:
    """判断是否是在未完成课程中询问是否继续学习。"""
    return "是否继续学习" in message and not _is_credit_completion_message(message)

def _check_page_dialogs(pg) -> bool:
    """只确认明确的学习成功弹框，返回 True 表示确认了学分结果。"""
    try:
        dlg = pg.locator(".el-message-box:visible")
        if dlg.count() > 0:
            # 课程完成后会提示已获得学分并询问是否继续当前课程。
            # 选择“否”结束当前课程，避免留在已完成的视频窗口。
            try:
                message = dlg.first.inner_text()
            except Exception:
                message = ""
            if _is_credit_completion_message(message):
                no_button = dlg.locator("button:has-text('否')")
                if no_button.count() > 0:
                    no_button.first.click()
                    print("课程已获得学分，已选择“否”结束当前课程")
                    return True

            # 普通提示不属于课程完成确认，交给专用清理函数处理。
            return False

    except Exception:
        pass
    return False


def _has_completion_dialog(context) -> bool:
    """只检测完成弹窗，不点击，避免播放监控提前消费确认状态。"""
    for pg in list(getattr(context, "pages", [])):
        try:
            dlg = pg.locator(".el-message-box:visible")
            if dlg.count() == 0:
                continue
            message = dlg.first.inner_text()
            if _is_credit_completion_message(message):
                return True
        except Exception:
            continue
    return False


def _dismiss_normal_dialogs(pg) -> bool:
    """关闭普通提示弹窗，但不把它们报告为课程完成。"""
    try:
        dlg = pg.locator(".el-message-box:visible")
        if dlg.count() > 0:
            message = dlg.first.inner_text()
            if _is_credit_completion_message(message):
                return False
            if _is_resume_learning_message(message):
                yes_button = dlg.locator(
                    "button:has-text('确定'), button:has-text('确认'), "
                    "button:has-text('继续'), .el-message-box__btns .el-button--primary"
                )
                if yes_button.count() > 0:
                    yes_button.first.click()
                    print("检测到课程未完成提示，已选择“确定”继续学习")
                    return True
            btn = dlg.locator(
                "button:has-text('确定'), button:has-text('确认'), "
                "button:has-text('继续'), button:has-text('我在'), "
                "button:has-text('知道了'), .el-message-box__btns .el-button--primary"
            )
            if btn.count() > 0:
                btn.first.click()
                print("已关闭普通 MessageBox 弹框")
                return True
        overlay = pg.locator(".el-overlay:visible button:has-text('确定')")
        if overlay.count() > 0:
            overlay.first.click()
            print("已关闭普通 overlay 弹框")
            return True
        dlg2 = pg.locator(
            "dialog[open] button:has-text('确定'), "
            "dialog[open] button:has-text('确认')"
        )
        if dlg2.count() > 0:
            dlg2.first.click()
            print("已关闭普通 HTML dialog 弹框")
            return True
    except Exception:
        pass
    return False


def _dismiss_playback_interruption_dialogs(context) -> bool:
    """确认播放中的在线提示，完成弹窗保留给主流程处理。"""
    handled = False
    for pg in list(getattr(context, "pages", [])):
        native_dialogs = getattr(pg, "_accepted_native_dialogs", [])
        completion_messages = []
        for message in list(native_dialogs):
            if _is_credit_completion_message(message):
                completion_messages.append(message)
            else:
                print(f"已确认播放中的原生提示: {message}")
                handled = True
        if native_dialogs:
            native_dialogs[:] = completion_messages
        if "about:blank" not in pg.url and _dismiss_normal_dialogs(pg):
            handled = True
    return handled


def dismiss_dialogs_all(context, timeout_sec: float = 0) -> None:
    """处理进入课程后可能异步出现的弹框，最多等待指定秒数。"""
    waited = 0.0
    while True:
        handled = False
        for pg in list(context.pages):
            if "about:blank" not in pg.url:
                handled = _check_page_dialogs(pg) or handled
                handled = _dismiss_normal_dialogs(pg) or handled
        if handled or waited >= timeout_sec:
            return
        pages = list(context.pages)
        if not pages:
            return
        pages[0].wait_for_timeout(250)
        waited += 0.25


def wait_and_dismiss_dialogs(context, timeout_sec: int = 15) -> bool:
    """等待并确认播放完成后出现的弹框。"""
    waited = 0
    while waited < timeout_sec:
        completion_confirmed = False
        for pg in list(context.pages):
            native_dialogs = getattr(pg, "_accepted_native_dialogs", [])
            if native_dialogs:
                message = native_dialogs.pop(0)
                if _is_credit_completion_message(message):
                    print(f"已确认学习完成原生弹框: {message}")
                    completion_confirmed = True
                else:
                    print(f"已确认普通原生弹框: {message}")
            if "about:blank" not in pg.url and _check_page_dialogs(pg):
                completion_confirmed = True
            if "about:blank" not in pg.url:
                _dismiss_normal_dialogs(pg)
        if completion_confirmed:
            # 给页面足够时间提交课程完成状态，避免确认后立即关闭页面。
            pages = list(context.pages)
            if pages:
                pages[0].wait_for_timeout(5000)
            print("已确认课程完成弹框")
            return True
        pages = list(context.pages)
        if pages:
            pages[0].wait_for_timeout(500)
        waited += 0.5
    return False


def has_credit_increased(before: dict, after: dict, category: str) -> bool:
    """判断目标类别学时是否被服务端实际记账。"""
    before_value = before.get("completed", {}).get(category)
    after_value = after.get("completed", {}).get(category)
    if before_value is None or after_value is None:
        raise RuntimeError(f"无法比较「{category}」学时，页面数据不完整")
    return after_value > before_value
