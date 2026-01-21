"""
阿里云OSS配置文件
请填写你的阿里云OSS信息后，将此文件重命名为 config.py
"""

# 阿里云OSS配置
OSS_ACCESS_KEY_ID = 'LTAI5t9St975sf9uRa4APQhU'
OSS_ACCESS_KEY_SECRET = '5Hy7Ilan7FzSXelxV3ZfE6VKlWU968'
OSS_ENDPOINT = 'https://oss-cn-shenzhen.aliyuncs.com'  # 根据你的地域修改
OSS_BUCKET_NAME = 'video-swap-test'

# 阿里云API配置
API_KEY = 'sk-238040cd14f843848beb2bfdfbf64acc'
API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis'

# 服务器配置
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

# 文件配置
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.mkv'}
