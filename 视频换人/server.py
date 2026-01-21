from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import time
import os
import uuid
import oss2
import json
import config

app = Flask(__name__)
CORS(app)

API_KEY = config.API_KEY
API_URL = config.API_URL

# 初始化OSS客户端
auth = oss2.Auth(config.OSS_ACCESS_KEY_ID, config.OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, config.OSS_ENDPOINT.replace('https://', ''), config.OSS_BUCKET_NAME)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件到阿里云OSS并返回URL"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > config.MAX_FILE_SIZE:
            return jsonify({'error': f'文件大小超过限制 ({config.MAX_FILE_SIZE / 1024 / 1024}MB)'}), 400
        
        # 检查文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in config.ALLOWED_EXTENSIONS:
            return jsonify({'error': f'不支持的文件类型: {file_ext}'}), 400
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        print(f"正在上传文件到OSS: {file.filename} -> {unique_filename}")
        
        # 上传到阿里云OSS
        try:
            bucket.put_object(unique_filename, file)
            
            # 生成公网可访问的URL
            file_url = f"https://{config.OSS_BUCKET_NAME}.{config.OSS_ENDPOINT.replace('https://', '')}/{unique_filename}"
            
            print(f"文件上传成功: {file_url}")
            
            return jsonify({
                'success': True,
                'url': file_url,
                'filename': unique_filename
            })
            
        except Exception as e:
            print(f"OSS上传失败: {str(e)}")
            return jsonify({'error': f'文件上传失败: {str(e)}'}), 500
        
    except Exception as e:
        print(f"上传文件时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/files/<filename>')
def get_file(filename):
    """获取上传的文件"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        data = request.json
        image_url = data.get('image_url')
        video_url = data.get('video_url')
        
        if not image_url or not video_url:
            print(f"错误: 缺少参数 - image_url: {image_url}, video_url: {video_url}")
            return jsonify({'error': '缺少image_url或video_url'}), 400
        
        print(f"收到生成请求 - image_url: {image_url}, video_url: {video_url}")
        
        # 提交任务
        headers = {
            "X-DashScope-Async": "enable",
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "wan2.2-animate-mix",
            "input": {
                "image_url": image_url,
                "video_url": video_url
            },
            "parameters": {
                "mode": "wan-std"
            }
        }
        
        print(f"正在提交任务到API: {API_URL}")
        print(f"请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('output', {}).get('task_id')
            print(f"任务提交成功，任务ID: {task_id}")
            return jsonify({
                'success': True,
                'task_id': task_id
            })
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"API请求失败: {error_data}")
            return jsonify({'error': f'API请求失败: {error_data}'}), response.status_code
            
    except Exception as e:
        print(f"生成视频时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """检查任务状态"""
    try:
        status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        
        response = requests.get(status_url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'data': result.get('output', {})
            })
        else:
            return jsonify({'error': f'查询状态失败: {response.status_code}'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("服务器启动在 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
