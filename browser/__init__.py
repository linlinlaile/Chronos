"""浏览器操作模块 — 自动启动 Chrome 并持久化登录状态"""

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from config import BROWSER_CHANNEL, CHROME_DEBUG_PORT, TARGET_URL, TIMEOUT, VIEWPORT

# 用户数据目录，持久化登录状态（cookie、localStorage 等）
USER_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data")
)


def launch_browser() -> tuple[Browser, BrowserContext, Page]:
    """启动 Google Chrome（使用持久化上下文保留登录状态）。

    Playwright 控制本机正式版 Chrome，首次运行后手动登录，后续自动恢复登录状态。

    返回:
        (browser, context, page)
    """
    print(f"用户数据目录: {USER_DATA_DIR}")
    print(f"正在启动 Google Chrome（channel={BROWSER_CHANNEL}）...")

    playwright = sync_playwright().start()

    attached = _try_attach_existing_chrome(playwright)
    if attached:
        browser, context, page = attached
        _inject_dialog_handler(context)
        context.on("page", lambda p: _inject_dialog_handler_for_page(p))
        print(f"已复用现有 Chrome 页面: {page.url}")
        return browser, context, page

    detached = _launch_detached_chrome(playwright)
    if detached:
        browser, context, page = detached
        _inject_dialog_handler(context)
        context.on("page", lambda p: _inject_dialog_handler_for_page(p))
        print(f"已启动独立 Chrome 页面: {page.url}")
        return browser, context, page

    # persistent context 会像普通 Chrome 一样保存所有数据
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        channel=BROWSER_CHANNEL,
        headless=False,
        viewport=VIEWPORT,
        args=[
            "--start-maximized",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
        ],
        # 接受下载，允许弹窗
        accept_downloads=True,
    )

    browser = playwright  # 保留 Playwright 生命周期，确保上下文持续有效

    pages = context.pages
    if pages:
        page = pages[0]
    else:
        page = context.new_page()

    # 在所有页面注入 JS 弹框自动点击
    _inject_dialog_handler(context)
    context.on("page", lambda p: _inject_dialog_handler_for_page(p))

    return browser, context, page


def _launch_detached_chrome(playwright):
    """独立启动 Chrome，再通过 CDP 连接，避免 Python 退出时关闭浏览器。"""
    candidates = [
        os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
    ]
    chrome = next((path for path in candidates if path and os.path.exists(path)), None)
    if not chrome:
        return None

    args = [
        chrome,
        f"--user-data-dir={USER_DATA_DIR}",
        f"--remote-debugging-port={CHROME_DEBUG_PORT}",
        "--start-maximized",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ]
    try:
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except OSError as exc:
        print(f"独立启动 Chrome 失败，将尝试 Playwright 管理模式: {exc}")
        return None

    for _ in range(40):
        attached = _try_attach_existing_chrome(playwright)
        if attached:
            return attached
        time.sleep(0.25)
    print("Chrome 调试端口启动超时，将尝试 Playwright 管理模式")
    return None


def _try_attach_existing_chrome(playwright):
    """连接脚本之前启动的 Chrome；普通未开启调试端口的 Chrome 不会被接管。"""
    endpoint = f"http://127.0.0.1:{CHROME_DEBUG_PORT}"
    try:
        with urllib.request.urlopen(f"{endpoint}/json/version", timeout=0.4) as response:
            json.load(response)
        browser = playwright.chromium.connect_over_cdp(endpoint)
    except Exception:
        return None

    contexts = browser.contexts
    if not contexts:
        return None
    context = contexts[0]
    pages = [p for p in context.pages if "learning.hzrs.hangzhou.gov.cn" in p.url]
    if not pages:
        return browser, context, context.new_page()

    # 优先复用已经登录的页面；登录检查函数在模块加载完成后可用。
    logged_page = next((p for p in pages if check_logged_in(p)), None)
    return browser, context, logged_page or pages[0]


def _inject_dialog_handler(context) -> None:
    """为 context 中所有已有页面注入弹框拦截。"""
    for pg in context.pages:
        _inject_dialog_handler_for_page(pg)


def _inject_dialog_handler_for_page(page) -> None:
    """按文案处理原生 confirm；DOM 弹框由主流程在正确时机处理。"""
    page._accepted_native_dialogs = []

    def accept_and_record(dialog) -> None:
        page._accepted_native_dialogs.append(dialog.message)
        print(f"检测到浏览器原生弹框: {dialog.message}")
        # 未完成课程需要“确定”继续；已获得学分时“取消”相当于选择“否”。
        if "是否继续学习" in dialog.message and (
            "获得学分" in dialog.message or "学习时间已达到要求" in dialog.message
        ):
            dialog.dismiss()
        else:
            dialog.accept()

    page.on("dialog", accept_and_record)


def check_logged_in(page: Page) -> bool:
    """检测是否已登录（必须同时满足域名 + 登录标志）。

    登录桥页面 zlb_login_bridge.html 也在 learning 域名下，但短暂显示
    "欢迎"文案，因此以「进入学时管理系统」按钮作为唯一可靠标志。
    """
    if "learning.hzrs.hangzhou.gov.cn" not in page.url:
        return False
    if "zlb_login_bridge" in page.url:
        return False

    # 唯一可靠标志：进入学时管理系统按钮（登录后首页才有）
    if page.locator("button:has-text('进入学时管理系统')").count() > 0:
        return True
    # 辅助：退出登录（登录后头部才有）
    if page.locator("text=退出登录").count() > 0:
        return True
    return False


def _find_logged_in_page(page: Page, context: BrowserContext | None = None):
    pages = context.pages if context else [page]
    for candidate in pages:
        try:
            if check_logged_in(candidate):
                return candidate
        except Exception:
            continue
    return None


def wait_for_login(page: Page, context: BrowserContext | None = None) -> Page:
    """等待用户手动登录，登录成功后再继续。

    用户点击「学员登录」→ 浙江政务网 SSO 回跳 → 自动回到已登录的课程界面。
    SSO 回跳有中间态（learning 页面短暂渲染但会话未稳定），需要二次确认。
    """
    logged_page = _find_logged_in_page(page, context)
    if logged_page:
        print("已登录，继续执行...")
        logged_page.bring_to_front()
        return logged_page

    print("\n" + "=" * 50)
    print("[!] 检测到未登录！请在浏览器中点击「学员登录」完成登录...")
    print("=" * 50 + "\n")

    # 轮询直到确认登录（连续两次检测通过，排除 SSO 中间态）
    confirmed = False
    waited = 0
    while not confirmed:
        logged_page = _find_logged_in_page(page, context)
        if logged_page:
            logged_page.bring_to_front()
            # 第一次检测通过，等 5 秒后再确认，避开回跳中间态
            print("  检测到登录信号，等待会话稳定...")
            logged_page.wait_for_timeout(5000)
            if check_logged_in(logged_page):
                confirmed = True
                page = logged_page
                break
            print("  会话不稳定，继续等待...")
        page.wait_for_timeout(3000)
        waited += 3
        if waited >= 15 and waited % 15 == 0:
            print(f"  已等待 {waited} 秒，仍在等待登录...")
        if waited > 300:
            raise Exception("等待登录超时（5分钟）")

    print("检测到已登录！\n")

    # 会话已稳定，用当前页面继续（SSO 回跳后通常已在课程页）
    if "learning.hzrs.hangzhou.gov.cn" not in page.url:
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=TIMEOUT)
    wait_page_ready(page)
    return page


def ensure_course_page(page: Page) -> None:
    """确保当前页面是课程列表页（#/Course），不是则跳转过去。"""
    current_url = page.url
    if "#/Course" not in current_url:
        print(f"正在跳转到课程页: {TARGET_URL}")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=TIMEOUT)
        wait_page_ready(page)
    else:
        print("当前已在课程页面，无需跳转")
        wait_page_ready(page)

    # 等待课程筛选区域渲染完成
    try:
        page.wait_for_selector(".selectList", timeout=15000)
        print("课程筛选区域已就绪")
    except Exception:
        print("课程筛选区域未渲染，稍后重试...")
        page.wait_for_timeout(3000)


def wait_page_ready(page: Page) -> None:
    """等待 SPA 页面加载完成。"""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
        print("页面网络请求完成")
    except Exception:
        print("页面加载超时（可能是 SPA 持续请求），继续执行...")

    page.wait_for_timeout(250)
    print(f"当前页面标题: {page.title()}")


def goto_url(page: Page, url: str) -> None:
    """导航到指定 URL 并等待加载完成。"""
    print(f"导航到: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)
    wait_page_ready(page)
