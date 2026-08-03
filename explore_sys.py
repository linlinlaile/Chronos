"""探索学时管理系统页面结构

打开浏览器 → 等待登录 → 点击「进入学时管理系统」→ dump 学时数据展示结构
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

D = os.path.join(os.getcwd(), "user_data")
TARGET = "https://learning.hzrs.hangzhou.gov.cn/#/Course"


def check_logged_in(pg) -> bool:
    if "learning.hzrs.hangzhou.gov.cn" not in pg.url or "zlb_login_bridge" in pg.url:
        return False
    if pg.locator("button:has-text('进入学时管理系统')").count() > 0:
        return True
    if pg.locator("text=退出登录").count() > 0:
        return True
    return False


def main():
    p = sync_playwright().start()
    ctx = p.chromium.launch_persistent_context(user_data_dir=D, headless=False, args=["--start-maximized"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()

    # 打开课程页
    pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
    try:
        pg.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    pg.wait_for_timeout(4000)

    # 等待登录
    print("=" * 60)
    print("[*] 若未登录，请在浏览器中点击「学员登录」完成登录")
    print("=" * 60)
    waited = 0
    while not check_logged_in(pg):
        pg.wait_for_timeout(3000)
        waited += 3
        if waited % 15 == 0 and waited > 0:
            print(f"  等待登录中... {waited}s")
    print("[OK] 已登录")

    # 确保在课程页
    pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(4000)

    # 点击 进入学时管理系统
    btn = pg.locator("button:has-text('进入学时管理系统')")
    print(f"进入学时管理系统按钮: {btn.count()}")
    if btn.count() == 0:
        print("未找到按钮！")
        pg.screenshot(path="explore_no_btn.png")
        ctx.close()
        return

    old_pages = set(ctx.pages)
    btn.first.click()
    pg.wait_for_timeout(8000)

    # 找新页面
    new_pages = [pp for pp in ctx.pages if pp not in old_pages and "about:blank" not in pp.url]
    print(f"新标签页: {len(new_pages)}")
    for i, pp in enumerate(ctx.pages):
        print(f"  [{i}] {pp.url} title={pp.title()}")

    sys_pg = None
    for pp in ctx.pages:
        if pp != pg and "about:blank" not in pp.url:
            sys_pg = pp
            break
    if not sys_pg:
        # 可能当前页跳转
        if pg.url != TARGET:
            sys_pg = pg

    if not sys_pg:
        print("未找到学时管理系统页面！")
        ctx.close()
        return

    sys_pg.bring_to_front()
    try:
        sys_pg.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    sys_pg.wait_for_timeout(6000)

    print(f"学时系统URL: {sys_pg.url}")
    print(f"学时系统Title: {sys_pg.title()}")

    # dump body 文本
    body = sys_pg.locator("body").inner_text()
    print("--- body 文本 (完整) ---")
    print(body)
    print("--- END ---")

    # 保存 HTML
    html = sys_pg.content()
    with open("sys_mgmt.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML 已保存: sys_mgmt.html ({len(html)} 字符)")

    # 截图
    sys_pg.screenshot(path="sys_mgmt.png", full_page=True)
    print("截图: sys_mgmt.png")

    # 分析主要区块
    print("\n--- 页面区块分析 ---")
    # 找所有数字 + 学时 相关
    import re
    numbers = re.findall(r"[\d.]+\s*(?:学时|学分)", body)
    print(f"学时/学分数字: {numbers[:20]}")

    # 找板块标题
    for kw in ["现已完成", "专业课程", "行业公需", "一般公需", "已完成", "要求", "目标"]:
        c = body.count(kw)
        if c > 0:
            print(f"  关键词[{kw}]: {c} 次")

    ctx.close()
    print("DONE")


if __name__ == "__main__":
    main()
