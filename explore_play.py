"""探索播放页面的学完机制

流程：登录 → 课程页选「一般公需」→ 查询 → 随机选课 → 立即学习 → dump播放页结构
只探索，不长时间运行。
"""
import os
import random
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

    pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
    try:
        pg.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    pg.wait_for_timeout(4000)

    if not check_logged_in(pg):
        print("[!] 未登录，请在浏览器中点击「学员登录」...")
        waited = 0
        while not check_logged_in(pg):
            pg.wait_for_timeout(3000)
            waited += 3
            if waited % 15 == 0 and waited > 0:
                print(f"  等待登录中... {waited}s")
    print("[OK] 已登录")

    # 确保课程页
    pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(4000)
    pg.wait_for_selector(".selectList", timeout=15000)

    # 选「一般公需」
    sl = pg.locator(".selectList").first
    sl.locator(".el-select").first.locator(".el-select__wrapper").click()
    pg.wait_for_timeout(500)
    pg.locator(".el-select__popper:visible .el-select-dropdown__item:has-text('一般公需')").first.click(force=True)
    pg.wait_for_timeout(500)
    print("[OK] 已选一般公需")

    # 查询
    pg.locator("button:has-text('查询')").first.click()
    pg.wait_for_timeout(4000)
    print("[OK] 查询完成")

    items = pg.locator(".itemBox")
    n = items.count()
    print(f"课程数: {n}")
    if n == 0:
        ctx.close()
        return

    # 随机选课
    chosen = items.nth(random.randint(0, n - 1))
    name = chosen.locator(".Line span").first.inner_text()
    print(f"选课: {name}")

    # 打开详情（新标签页）
    with ctx.expect_page(timeout=30000) as info:
        chosen.locator("img").first.click()
    detail = info.value
    detail.bring_to_front()
    try:
        detail.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    detail.wait_for_timeout(4000)
    print(f"详情页: {detail.url}")

    # 等立即学习
    try:
        detail.wait_for_selector("button:has-text('立即学习')", timeout=30000)
        detail.locator("button:has-text('立即学习')").first.click()
        print("[OK] 点击立即学习")
    except Exception as e:
        print(f"立即学习按钮问题: {e}")
    detail.wait_for_timeout(5000)

    # 找播放页
    play_pg = detail
    for pp in ctx.pages:
        if "class" in pp.url.lower():
            play_pg = pp
            break
    play_pg.bring_to_front()
    play_pg.wait_for_timeout(3000)
    print(f"播放页URL: {play_pg.url}")

    # dump 播放页按钮
    print("\n--- 播放页按钮 ---")
    for i in range(play_pg.locator("button").count()):
        b = play_pg.locator("button").nth(i)
        t = b.inner_text().strip() or "(空)"
        if t:
            print(f"  [{i}] {t}")

    # video/iframe
    print(f"video: {play_pg.locator('video').count()}, iframe: {play_pg.locator('iframe').count()}")

    # body 文本前2000
    print("\n--- body 前2000 ---")
    print(play_pg.locator("body").inner_text()[:2000])

    # 截图
    play_pg.screenshot(path="play_page.png", full_page=True)
    print("\n截图: play_page.png")

    # 保存HTML
    html = play_pg.content()
    with open("play_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML: play_page.html ({len(html)}字符)")

    ctx.close()
    print("DONE")


if __name__ == "__main__":
    main()
