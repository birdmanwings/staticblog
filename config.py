"""配置文件"""
import os

SECRET_KEY = 'test'

# 站点主标题
SITE_TITLE = 'BDWMS の 闲语'
# 站点副标题
SITE_SUBTITLE = '未来有一个人在等待'

# 文章md文件
POST_PATH = './source/_posts/'
# 页面md文件
PAGE_PATH = './source/_pages/'

# 转换为html的文件
GENERATED_PATH = './staticblog/static/generated/'
# 默认分类
DEFAULT_CATEGORY = '未分类'
# 默认标签
DEFAULT_TAG = ['其他']

# 存放shelve数据文件
BLOG_DAT = './staticblog/static/generated/data.dat'

# 管理员登录名及密码
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME') or 'test'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD') or 'test123456'
