# 输出结果目录

存放所有仿真运行结果和分析输出。

## 📁 目录结构

```
outputs/
├── simulation_results/  # 仿真原始结果
├── analysis/           # 分析处理结果
├── visualizations/     # 图表和动画
└── exports/           # 导出的报告和数据
```

## 📂 子目录说明

### `simulation_results/` - 仿真结果
- **用途**: 存放仿真程序直接输出的原始数据
- **格式**: CSV, JSON, Parquet等
- **内容**:
  - 车辆轨迹数据
  - 订单完成记录
  - 充电站使用情况
  - 系统性能指标
  - 实时状态快照

### `analysis/` - 分析结果
- **用途**: 存放对仿真数据进行分析后的结果
- **格式**: CSV, JSON, Excel等
- **内容**:
  - 统计分析结果
  - 性能评估报告
  - 趋势分析数据
  - 对比分析结果
  - 优化建议数据

### `visualizations/` - 可视化输出
- **用途**: 存放图表、动画和其他可视化内容
- **格式**: PNG, SVG, HTML, GIF, MP4等
- **内容**:
  - 仿真过程动画
  - 统计图表
  - 热力图
  - 轨迹可视化
  - 交互式图表

### `exports/` - 导出文件
- **用途**: 存放最终的报告和对外分享的数据
- **格式**: PDF, Excel, Word, ZIP等
- **内容**:
  - 仿真报告
  - 数据汇总表
  - 演示文稿
  - 压缩的数据包

## 📝 使用规范

### 文件命名规则
```
类型_配置_时间戳.格式
例如: simulation_20vehicles_20250524_143022.csv
     analysis_performance_20250524.xlsx
     viz_trajectory_west_lafayette_20250524.html
```

### 目录组织建议
- 按日期创建子文件夹: `YYYY-MM-DD/`
- 按实验配置分组: `实验名称/`
- 重要结果单独标记: `IMPORTANT_结果描述/`

### 数据标注
```
outputs/
├── simulation_results/
│   ├── 2025-05-24/
│   │   ├── run_001_baseline/
│   │   ├── run_002_high_demand/
│   │   └── README.md          # 记录实验配置
│   └── IMPORTANT_validation_results/
```

## 🔍 典型输出内容

### 仿真结果文件
- `vehicle_trajectories.csv` - 车辆移动轨迹
- `order_records.csv` - 订单处理记录
- `charging_logs.csv` - 充电事件日志
- `metrics_summary.json` - 关键指标汇总
- `system_state_snapshots.parquet` - 系统状态快照

### 分析结果文件
- `performance_analysis.xlsx` - 性能分析表格
- `efficiency_metrics.csv` - 效率指标
- `comparison_results.json` - 对比分析结果
- `optimization_suggestions.md` - 优化建议

### 可视化文件
- `simulation_animation.html` - 仿真动画
- `performance_charts.png` - 性能图表
- `heatmap_demand.svg` - 需求热力图
- `trajectory_plot.png` - 轨迹图

## 🎯 快速访问

### 最新结果
```bash
# 查看最新仿真结果
ls -la outputs/simulation_results/ | tail -5

# 查看最新分析
ls -la outputs/analysis/ | tail -5
```

### 重要结果
- 验证实验结果: `simulation_results/IMPORTANT_validation_results/`
- 基准性能数据: `analysis/IMPORTANT_baseline_performance/`
- 关键可视化: `visualizations/IMPORTANT_key_visuals/`

## 📊 数据管理

### 自动清理
- 定期清理临时文件和中间结果
- 保留重要的基准数据和验证结果
- 压缩旧的大文件以节省空间

### 备份策略
- 重要结果备份到云存储
- 定期压缩和归档旧结果
- 保留完整的实验记录

### 数据追溯
- 记录生成每个结果的仿真配置
- 保留代码版本信息
- 记录数据处理步骤

## ⚙️ 集成说明

### 与main.py的集成
```python
# 在main.py中使用outputs目录
output_dir = "outputs/simulation_results"
data_manager = DataManager(output_dir)

# 保存结果时自动创建时间戳文件夹
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result_path = f"{output_dir}/{timestamp}/"
```

### 与数据分析的集成
- 分析脚本自动读取`simulation_results/`中的数据
- 结果保存到`analysis/`对应文件夹
- 生成的图表保存到`visualizations/`

## ⚠️ 注意事项

1. **存储空间**: 仿真结果可能很大，定期清理不需要的文件
2. **文件权限**: 确保有足够的写入权限
3. **数据安全**: 敏感结果不要提交到版本控制
4. **结果验证**: 重要结果要进行验证和备份

---

**最后更新**: 2025-05-24  
**维护者**: 项目团队 