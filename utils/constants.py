"""常量配置文件：统一管理可配置项，便于修改"""

# 系统配置
SYSTEM_NAME = "学生党建信息管理系统"
SYSTEM_ICON = "🏫"
DEFAULT_ORG_NAME = "高校学生第一党支部"

# 数据存储配置
DATA_FILE_PATH = "student_party_data.json"  # 数据文件路径

# 界面配置
PAGE_LAYOUT = "wide"  # Streamlit页面布局（wide/centered）
MAX_RECORD_DISPLAY = 5  # 流程记录最多显示条数

# 业务规则常量
MIN_TRAINERS_COUNT = 1  # 培养联系人最少人数
MAX_TRAINERS_COUNT = 2  # 培养联系人最多人数
INTRODUCERS_REQUIRED = 2  # 入党介绍人必填人数
PROBATION_PERIOD_DAYS = 365  # 预备期（天）
REVIEW_REQUIRED_COUNT = 2  # 积极分子转发展对象所需考察次数
