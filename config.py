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

# 截图保存路径
SCREENSHOT_PATH = "screenshot.png"

# === 学时目标（年度要求） ===
# 专业课程、行业公需、一般公需 各自需要达到的学时
CREDIT_REQUIREMENTS = {
    "专业课程": 60.0,
    "行业公需": 30.0,
    "一般公需": 30.0,
}

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
