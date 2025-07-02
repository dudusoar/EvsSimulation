# Webapp启动故障排除指南

## 🚨 **关键问题：ModuleNotFoundError**

### 问题现象
```bash
ModuleNotFoundError: No module named 'models.vehicle'
```

### 根本原因
**工作目录和Python路径问题**：

1. **正确方式**：`uvicorn webapp.backend.main:app`
   - 在**项目根目录**运行
   - Python自动把当前目录加入sys.path
   - 可以找到 `models/vehicle.py`

2. **错误方式**：`python webapp/run.py`
   - run.py内部切换到`backend/`目录
   - Python找不到项目根目录的模块
   - uvicorn的子进程无法继承父进程的sys.path设置

### 解决方案

#### ✅ **推荐方式（项目根目录）**
```bash
# 1. 激活虚拟环境
.venv\Scripts\Activate.ps1

# 2. 在项目根目录运行
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload
```

#### ❌ **避免使用**
```bash
# 这个方式会导致模块找不到
python webapp/run.py
```

## 🔧 **完整启动流程**

### 1. 环境准备
```bash
# 确保在项目根目录
cd E:\Code\Github\EvsSimulation

# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 验证虚拟环境激活（命令提示符前应有 (EvsSimulation)）
```

### 2. 启动webapp
```bash
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload
```

### 3. 访问地址
- **主界面**: http://127.0.0.1:8080
- **API文档**: http://127.0.0.1:8080/docs
- **WebSocket**: ws://127.0.0.1:8080/ws/simulation

## 🐛 **常见问题排查**

### Q1: 端口被占用
```bash
# 检查端口占用
netstat -an | findstr :8080

# 终止占用进程
taskkill /f /im python.exe
```

### Q2: 虚拟环境未激活
```bash
# 症状：命令提示符前没有 (EvsSimulation)
# 解决：重新激活虚拟环境
.venv\Scripts\Activate.ps1
```

### Q3: 找不到uvicorn命令
```bash
# 确保虚拟环境已激活并安装了依赖
pip install -r webapp/backend/requirements.txt
```

### Q4: 依赖包缺失
```bash
# 安装webapp后端依赖
pip install fastapi uvicorn websockets pydantic

# 或安装完整项目依赖
pip install -r requirements.txt
```

## 📁 **目录结构说明**

```
EvsSimulation/              ← 项目根目录（在这里运行uvicorn）
├── models/                 ← Python需要找到这个目录
│   └── vehicle.py
├── core/
├── webapp/
│   ├── backend/           ← 不要在这个目录运行
│   │   └── main.py
│   └── run.py             ← 不要使用这个脚本
└── .venv/
```

## 🎯 **最佳实践**

1. **始终在项目根目录运行uvicorn命令**
2. **确保虚拟环境已激活**
3. **使用统一的地址 127.0.0.1:8080**
4. **不要使用 run.py 脚本**

## 🔍 **调试技巧**

### 验证Python路径
```bash
# 在项目根目录测试模块导入
python -c "from models.vehicle import Vehicle; print('SUCCESS')"
```

### 检查当前工作目录
```bash
# 确保在正确目录
pwd
# 或
echo $PWD
```

### 查看Python搜索路径
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

## 📝 **更新记录**

- **2024-01-XX**: 统一使用 127.0.0.1:8080 地址
- **2024-01-XX**: 废弃 run.py 启动方式
- **2024-01-XX**: 添加详细故障排除指南 