# 安装指南

## 1. 环境准备

### 创建虚拟环境并安装依赖包

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-app.txt
```

## 2. 模型下载

### 下载所有模型文件

```bash
python scripts/download_model.py --models all
```

### 模型文件存储目录

模型文件将下载到以下目录：

- `./hivision/creator/retinaface/weights/` - 1个模型文件
- `./hivision/creator/weights/` - 4个模型文件

## 3. 运行应用

### 启动后台服务

```bash
python app.py
```

## 4. Linux环境额外配置

如果在Linux环境下运行，需要安装UI相关依赖，否则会出现`libGL.so`错误：

```bash
dnf install -y mesa-libGL
```

## 5. API服务部署

### 部署API服务

```bash
python deploy_api.py