"""浏览器操作模块 — 自动启动 Chrome 并持久化登录状态"""

import os
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from config import TARGET_URL, TIMEOUT, VIEWPORT

# 用户数据目录，持久化登录状态（cookie、localStorage 等）
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data")


def launch_browser() -> tuple[Browser, BrowserContext, Page]:
    """启动 Chromium 浏览器（使用持久化上下文保留登录状态）。

    Playwright 使用内置 Chromium，首次运行后手动登录，后续自动恢复登录状态。

    返回:
        (browser, context, page)
    """
    print(f"用户数据目录: {USER_DATA_DIR}")
    print("正在启动浏览器...")

    playwright = sync_playwright().start()

    # persistent context 会像普通 Chrome 一样保存所有数据
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        viewport=VIEWPORT,
        args=["--start-maximized"],
        # 接受下载，允许弹窗
        accept_downloads=True,
    )

    browser = None  # persistent context 模式下不需要显式管理 browser

    pages = context.pages
    if pages:
        page = pages[0]
    else:
        page = context.new_page()

    # 在所有页面注入 JS 弹框自动点击
    _inject_dialog_handler(context)
    context.on("page", lambda p: _inject_dialog_handler_for_page(p))

    return browser, context, page


def _inject_dialog_handler(context) -> None:
    """为 context 中所有已有页面注入弹框拦截。"""
    for pg in context.pages:
        _inject_dialog_handler_for_page(pg)


def _inject_dialog_handler_for_page(page) -> None:
    """注入 JS 自动关闭 Element UI 弹框 + 原生 alert/confirm。"""
    page.on("dialog", lambda d: d.accept())
    try:
        page.evaluate("""
            if (!window.__dialog_handler_injected) {
                window.__dialog_handler_injected = true;
                setInterval(function() {
                    var btns = document.querySelectorAll(
                        '.el-message-box__wrapper button, .el-overlay button, .el-dialog__wrapper button'
                    );
                    for (var i = 0; i < btns.length; i++) {
                        if (btns[i].textContent.indexOf('确定') !== -1 ||
                            btns[i].textContent.indexOf('确认') !== -1 ||
                            btns[i].textContent.indexOf('同意') !== -1 ||
                            btns[i].textContent.indexOf('知道了') !== -1) {
                            btns[i].click();
                        }
                    }
                }, 2000);
            }
        """)
    except Exception:
        pass


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


def wait_for_login(page: Page) -> None:
    """等待用户手动登录，登录成功后再继续。

    用户点击「学员登录」→ 浙江政务网 SSO 回跳 → 自动回到已登录的课程界面。
    SSO 回跳有中间态（learning 页面短暂渲染但会话未稳定），需要二次确认。
    """
    if check_logged_in(page):
        print("已登录，继续执行...")
        return

    print("\n" + "=" * 50)
    print("[!] 检测到未登录！请在浏览器中点击「学员登录」完成登录...")
    print("=" * 50 + "\n")

    # 轮询直到确认登录（连续两次检测通过，排除 SSO 中间态）
    confirmed = False
    waited = 0
    while not confirmed:
        if check_logged_in(page):
            # 第一次检测通过，等 5 秒后再确认，避开回跳中间态
            print("  检测到登录信号，等待会话稳定...")
            page.wait_for_timeout(5000)
            if check_logged_in(page):
                confirmed = True
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
        page.wait_for_load_state("networkidle", timeout=TIMEOUT)
        print("页面网络请求完成")
    except Exception:
        print("页面加载超时（可能是 SPA 持续请求），继续执行...")

    page.wait_for_timeout(1500)
    print(f"当前页面标题: {page.title()}")


def goto_url(page: Page, url: str) -> None:
    """导航到指定 URL 并等待加载完成。"""
    print(f"导航到: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)
    wait_page_ready(page)
