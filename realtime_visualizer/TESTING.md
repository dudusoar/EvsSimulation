# 实时可视化测试脚本说明

本目录包含了各种测试脚本，用于验证实时可视化功能的不同方面。

## 📋 **测试脚本概览**

### 🧪 `test_flask_simple.py`
**推荐使用** - 最简单直接的Flask API测试

**用途：**
- 快速测试Flask API服务器
- 验证路由注册是否正确
- 查看所有可用的API端点

**运行方法：**
```bash
cd EvsSimulation
.\.venv\Scripts\python.exe realtime_visualizer/test_flask_simple.py
```

**输出：**
- 显示所有注册的API路由
- 启动服务器在 http://localhost:8080
- 提供API端点列表

---

### 📡 `test_api_endpoints.py`
**独立API测试** - 测试API端点是否响应

**用途：**
- 在服务器运行时测试API端点
- 验证API返回的状态码和数据
- 无需前端即可测试后端

**运行方法：**
```bash
# 先启动Flask服务器（使用其他测试脚本）
# 然后在另一个终端运行：
cd EvsSimulation
.\.venv\Scripts\python.exe realtime_visualizer/test_api_endpoints.py
```

---

### 🚀 `test_flask_api.py`
**完整功能测试** - 测试整个Flask API实时可视化系统

**用途：**
- 全面的依赖项检查
- 完整的导入测试
- 启动完整的实时可视化系统

**运行方法：**
```bash
cd EvsSimulation
.\.venv\Scripts\python.exe realtime_visualizer/test_flask_api.py
```

**功能：**
- ✅ 检查Flask、CORS等依赖
- ✅ 验证所有文件存在
- ✅ 测试模块导入
- 🚀 启动完整系统

---

### 📡 `test_realtime.py`
**WebSocket版本测试** - 原始WebSocket实现测试（已过时）

**状态：** ⚠️ 已知问题 - WebSocket服务器启动失败

**用途：**
- 测试原始WebSocket实现
- 已被Flask API方案替代
- 保留用于对比参考

---

## 🎯 **推荐测试流程**

### 1️⃣ **快速验证**
```bash
cd EvsSimulation
.\.venv\Scripts\python.exe realtime_visualizer/test_flask_simple.py
```

### 2️⃣ **访问前端**
打开浏览器访问：http://localhost:8080

### 3️⃣ **API测试**（可选）
在另一个终端：
```bash
.\.venv\Scripts\python.exe realtime_visualizer/test_api_endpoints.py
```

## 🔧 **故障排除**

### 问题：API返回404
**解决：** 确保使用 `test_flask_simple.py` 启动，它会显示所有注册的路由

### 问题：前端无法连接
**解决：** 检查Console中的错误信息，确保API服务器正在运行

### 问题：导入错误
**解决：** 确保在EvsSimulation根目录运行，且虚拟环境已激活

## 📊 **当前状态**

- ✅ **Flask API方案** - 工作正常，稳定可靠
- ❌ **WebSocket方案** - 事件循环问题，已暂停使用
- ✅ **前端界面** - HTTP轮询，2秒更新间隔
- ✅ **仿真引擎** - 完全集成，真实数据

## 🎮 **使用建议**

1. **开发测试**：使用 `test_flask_simple.py`
2. **演示展示**：使用 `test_flask_api.py`
3. **API调试**：使用 `test_api_endpoints.py`
4. **避免使用**：`test_realtime.py`（已过时） 