"""测试：播放完成后页面的行为

进入课程 → 播放 → 监听 video ended → 观察学完后的页面行为
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
        print("[!] 未登录，请点击学员登录...")
        while not check_logged_in(pg):
            pg.wait_for_timeout(3000)
    print("[OK] 已登录")

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

    pg.locator("button:has-text('查询')").first.click()
    pg.wait_for_timeout(4000)

    items = pg.locator(".itemBox")
    n = items.count()
    print(f"课程数: {n}")
    if n == 0:
        ctx.close()
        return

    chosen = items.nth(random.randint(0, n - 1))
    name = chosen.locator(".Line span").first.inner_text()
    print(f"选课: {name}")

    with ctx.expect_page(timeout=30000) as info:
        chosen.locator("img").first.click()
    detail = info.value
    detail.bring_to_front()
    try:
        detail.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    detail.wait_for_timeout(4000)

    detail.wait_for_selector("button:has-text('立即学习')", timeout=30000)
    detail.locator("button:has-text('立即学习')").first.click()
    detail.wait_for_timeout(5000)
    print("[OK] 立即学习")

    # 找播放页
    play_pg = detail
    for pp in ctx.pages:
        if "class" in pp.url.lower():
            play_pg = pp
            break
    play_pg.bring_to_front()
    play_pg.wait_for_timeout(2000)
    print(f"播放页: {play_pg.url}")

    # 注入 JS 监听 video ended 和进度上报
    play_pg.evaluate("""
        window.__ended = false;
        window.__played_seconds = 0;
        const v = document.querySelector('video');
        if (v) {
            window.__video = v;
            v.addEventListener('timeupdate', () => {
                window.__played_seconds = v.currentTime;
            });
            v.addEventListener('ended', () => {
                window.__ended = true;
                console.log('VIDEO ENDED');
            });
            // 播放
            v.play().catch(e => console.log('play error', e));
            // 点击 Play Video 按钮（Video.js 大按钮）
            const btn = document.querySelector('.vjs-big-play-button');
            if (btn) btn.click();
        }
    """)
    print("[OK] 已触发播放，监听中...")

    # 读取视频时长
    dur = play_pg.evaluate("document.querySelector('video') ? document.querySelector('video').duration : 0")
    print(f"视频时长: {dur:.1f} 秒")

    # 轮询等待 ended（最多等 dur + 30 秒），同时监听页面变化
    import time
    waited = 0
    max_wait = int(dur) + 30
    while waited < max_wait:
        play_pg.wait_for_timeout(10000)
        waited += 10
        state = play_pg.evaluate("({ended: window.__ended, sec: window.__played_seconds, paused: document.querySelector('video') ? document.querySelector('video').paused : null, current: document.querySelector('video') ? document.querySelector('video').currentTime : null})")
        print(f"  [{waited}s] ended={state['ended']} current={state['current']:.1f}/{dur:.1f}")
        if state["ended"]:
            print("[!] 视频播放完成 (ended)")
            # 观察页面状态
            play_pg.wait_for_timeout(5000)
            print("  结束后URL:", play_pg.url)
            print("  结束后按钮:")
            for i in range(play_pg.locator("button").count()):
                t = play_pg.locator("button").nth(i).inner_text().strip() or "(空)"
                if t:
                    print(f"    [{i}] {t}")
            # 检查弹窗
            print("  MessageBox:", play_pg.locator(".el-message-box").count())
            print("  Overlay:", play_pg.locator(".el-overlay").count())
            break

    play_pg.screenshot(path="after_ended.png", full_page=True)
    print("截图: after_ended.png")
    ctx.close()
    print("DONE")


if __name__ == "__main__":
    main()
