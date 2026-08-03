"""快速验证：进入一般公需课程 → 播放 → 检查进度读取是否正常（不长时间等）"""
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
    pg.wait_for_timeout(4000)

    if not check_logged_in(pg):
        print("[!] 未登录，请点击学员登录...")
        while not check_logged_in(pg):
            pg.wait_for_timeout(3000)
    print("[OK] 已登录")

    pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(4000)
    pg.wait_for_selector(".selectList", timeout=15000)

    # 选一般公需
    sl = pg.locator(".selectList").first
    sl.locator(".el-select").first.locator(".el-select__wrapper").click()
    pg.wait_for_timeout(500)
    pg.locator(".el-select__popper:visible .el-select-dropdown__item:has-text('一般公需')").first.click(force=True)
    pg.wait_for_timeout(500)
    pg.locator("button:has-text('查询')").first.click()
    pg.wait_for_timeout(4000)

    items = pg.locator(".itemBox")
    n = items.count()
    print(f"课程数: {n}")
    chosen = items.nth(random.randint(0, n - 1))
    name = chosen.locator(".Line span").first.inner_text()
    print(f"选课: {name}")

    with ctx.expect_page(timeout=30000) as info:
        chosen.locator("img").first.click()
    detail = info.value
    detail.bring_to_front()
    detail.wait_for_timeout(4000)

    detail.wait_for_selector("button:has-text('立即学习')", timeout=30000)
    detail.locator("button:has-text('立即学习')").first.click()
    detail.wait_for_timeout(5000)
    print("[OK] 立即学习")

    # 找播放页
    play_pg = None
    for pp in ctx.pages:
        if "/class" in pp.url:
            play_pg = pp
            break
    if not play_pg:
        play_pg = detail
    play_pg.bring_to_front()
    play_pg.wait_for_timeout(3000)
    print(f"播放页: {play_pg.url}")

    # 点击 Play Video
    btn = play_pg.locator("button:has-text('Play Video')")
    print(f"Play Video 按钮: {btn.count()}")
    if btn.count() > 0:
        btn.first.click()
        print("[OK] 点击 Play Video")
        play_pg.wait_for_timeout(5000)

    # 检查 video 状态
    state = play_pg.evaluate("""() => {
        const v = document.querySelector('video');
        if (!v) return {exists: false};
        return {
            exists: true,
            paused: v.paused,
            current: v.currentTime,
            duration: v.duration,
            readyState: v.readyState,
            src: v.src
        };
    }""")
    print("video 状态:", state)

    play_pg.screenshot(path="verify_play.png", full_page=False)
    print("截图: verify_play.png")

    ctx.close()
    print("DONE")


if __name__ == "__main__":
    main()
