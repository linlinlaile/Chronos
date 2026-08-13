"""配置文件"""

# 目标网址
TARGET_URL = "https://learning.hzrs.hangzhou.gov.cn/#/Course"

# 学时管理系统首页
CREDIT_SYSTEM_URL = "https://learning.hzrs.hangzhou.gov.cn/#/backIndex"

# 页面视口大小
VIEWPORT = {
    "width": 1280,
    "height": 720,
}

# 超时设置（毫秒）
TIMEOUT = 30_000

# 使用本机安装的正式版 Google Chrome，而不是 Playwright 内置 Chromium。
BROWSER_CHANNEL = "chrome"

# 让后续运行可以复用本脚本之前启动的 Chrome。仅监听本机回环地址。
CHROME_DEBUG_PORT = 9222

# 任务完成或发生错误后仍保持浏览器窗口和进程打开，便于查看现场。
KEEP_BROWSER_OPEN = True

# 截图保存路径
SCREENSHOT_PATH = "screenshot.png"

# 正常播放不保存截图，仅在失败分支保留诊断现场。
SAVE_PLAYBACK_SCREENSHOTS = False

# === 学时目标（年度要求） ===
# 专业课程、行业公需、一般公需 各自需要达到的学时
CREDIT_REQUIREMENTS = {
    "专业课程": 60.0,
    "行业公需": 30.0,
    "一般公需": 30.0,
}

# 连续学习多少门课程后再刷新一次学时面板，避免每门课结束都切回学时页。
CREDIT_CHECK_INTERVAL = 5

# 课程目录搜索范围，仅首次在第 1 到第 5 页建立课程队列。
COURSE_PAGE_END = 5

# 随机分页时允许的最大分页操作次数，避免远距离页码退化为长时间逐页点击。
MAX_PAGE_NAVIGATION_STEPS = 12

# 单轮最多连续尝试的候选课程数；失败课程不会写入完成记录。
MAX_COURSE_ATTEMPTS = 3

# 学时性价比组合搜索上限；超出时使用确定性的时长/效率降级排序。
CREDIT_SELECTION_MAX_CANDIDATES = 80
CREDIT_HOUR_PRECISION = 0.5
CREDIT_UNKNOWN_FALLBACK = True

# 已完成课程记录，脚本重启后继续避免重复学习。
LEARNED_COURSES_FILE = "learned_courses.json"

# 首次扫描后保存每个课程类别的课程页码、位置和时长。
COURSE_CATALOG_FILE = "course_catalog.json"

# === 页面元素标识 ===

# 课程类别下拉框
COURSE_CATEGORY_LABEL = "课程类别"

# 下拉选项文本（可选类别）
CATEGORY_OPTIONS = ["专业课程", "行业公需", "一般公需"]

# 查询按钮文本
QUERY_BUTTON_TEXT = "查询"

# 立即学习按钮文本
LEARN_NOW_TEXT = "立即学习"

# 进入学时管理系统按钮
ENTER_CREDIT_SYSTEM = "进入学时管理系统"

# 进入在线学习系统按钮（学时系统返回课程页）
BACK_TO_LEARNING = "进入在线学习系统"
