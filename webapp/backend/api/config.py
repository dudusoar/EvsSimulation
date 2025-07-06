"""
Configuration Management API Endpoints
支持YAML配置文件的管理，实现前后端统一配置
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from webapp.backend.models.response import APIResponse
from config.yaml_config_manager import config_manager, SimulationConfigModel
from config.simulation_config import convert_dict_to_yaml
from pydantic import BaseModel, ValidationError
import json

router = APIRouter()


class ConfigCreateRequest(BaseModel):
    """创建配置请求"""
    name: str
    config_data: Dict[str, Any]


class ConfigUpdateRequest(BaseModel):
    """更新配置请求"""
    config_data: Dict[str, Any]


class ConfigValidationRequest(BaseModel):
    """配置验证请求"""
    config_data: Dict[str, Any]


@router.get("/list", response_model=APIResponse)
async def list_configurations():
    """列出所有可用的配置文件"""
    try:
        config_files = config_manager.list_configs()
        
        # 获取每个配置文件的基本信息
        configs_info = []
        for config_file in config_files:
            try:
                config = config_manager.load_config(config_file)
                info = {
                    "filename": config_file,
                    "name": config.simulation.name,
                    "location": config.simulation.location,
                    "vehicles": config.vehicles.count,
                    "duration": config.simulation.duration,
                    "created_at": config.metadata.get('loaded_at', 'Unknown')
                }
                configs_info.append(info)
            except Exception as e:
                # 如果某个配置文件损坏，记录错误但继续处理其他文件
                configs_info.append({
                    "filename": config_file,
                    "name": "配置文件损坏",
                    "error": str(e)
                })
        
        return APIResponse(
            success=True,
            message=f"找到 {len(configs_info)} 个配置文件",
            data={"configurations": configs_info}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置列表失败: {str(e)}")


@router.post("/create", response_model=APIResponse)
async def create_configuration(request: ConfigCreateRequest):
    """创建新的配置文件"""
    try:
        # 验证配置文件名
        if not request.name.endswith('.yaml'):
            request.name += '.yaml'
        
        # 检查文件是否已存在
        existing_configs = config_manager.list_configs()
        if request.name in existing_configs:
            return APIResponse(
                success=False,
                message="配置文件已存在",
                error=f"配置文件 {request.name} 已经存在"
            )
        
        # 转换配置数据为YAML模型
        try:
            if 'simulation' in request.config_data:
                # 已经是新格式
                config_model = SimulationConfigModel(**request.config_data)
            else:
                # 传统格式，需要转换
                config_model = convert_dict_to_yaml(request.config_data)
        except ValidationError as e:
            return APIResponse(
                success=False,
                message="配置数据验证失败",
                error=f"配置验证错误: {str(e)}"
            )
        
        # 保存配置文件
        success = config_manager.save_config(config_model, request.name)
        
        if success:
            return APIResponse(
                success=True,
                message=f"配置文件 {request.name} 创建成功",
                data={"filename": request.name, "config": config_model.dict()}
            )
        else:
            return APIResponse(
                success=False,
                message="保存配置文件失败",
                error="无法写入配置文件"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建配置失败: {str(e)}")


@router.get("/{config_name}", response_model=APIResponse)
async def get_configuration(config_name: str):
    """获取指定的配置文件"""
    try:
        # 确保文件名有正确的扩展名
        if not config_name.endswith('.yaml'):
            config_name += '.yaml'
        
        config = config_manager.load_config(config_name)
        
        return APIResponse(
            success=True,
            message=f"配置 {config_name} 加载成功",
            data={
                "filename": config_name,
                "config": config.dict(),
                "yaml_format": True
            }
        )
        
    except FileNotFoundError:
        return APIResponse(
            success=False,
            message="配置文件不存在",
            error=f"找不到配置文件: {config_name}"
        )
    except ValidationError as e:
        return APIResponse(
            success=False,
            message="配置文件格式错误",
            error=f"配置验证失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.put("/{config_name}", response_model=APIResponse)
async def update_configuration(config_name: str, request: ConfigUpdateRequest):
    """更新指定的配置文件"""
    try:
        # 确保文件名有正确的扩展名
        if not config_name.endswith('.yaml'):
            config_name += '.yaml'
        
        # 检查配置文件是否存在
        existing_configs = config_manager.list_configs()
        if config_name not in existing_configs:
            return APIResponse(
                success=False,
                message="配置文件不存在",
                error=f"找不到配置文件: {config_name}"
            )
        
        # 转换和验证配置数据
        try:
            if 'simulation' in request.config_data:
                # 已经是新格式
                config_model = SimulationConfigModel(**request.config_data)
            else:
                # 传统格式，需要转换
                config_model = convert_dict_to_yaml(request.config_data)
        except ValidationError as e:
            return APIResponse(
                success=False,
                message="配置数据验证失败",
                error=f"配置验证错误: {str(e)}"
            )
        
        # 保存更新的配置
        success = config_manager.save_config(config_model, config_name)
        
        if success:
            return APIResponse(
                success=True,
                message=f"配置文件 {config_name} 更新成功",
                data={"filename": config_name, "config": config_model.dict()}
            )
        else:
            return APIResponse(
                success=False,
                message="保存配置文件失败",
                error="无法写入配置文件"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete("/{config_name}", response_model=APIResponse)
async def delete_configuration(config_name: str):
    """删除指定的配置文件"""
    try:
        # 确保文件名有正确的扩展名
        if not config_name.endswith('.yaml'):
            config_name += '.yaml'
        
        # 不允许删除默认配置
        if config_name == "default.yaml":
            return APIResponse(
                success=False,
                message="不能删除默认配置",
                error="default.yaml 是系统默认配置，不能删除"
            )
        
        config_path = config_manager.config_dir / config_name
        
        if not config_path.exists():
            return APIResponse(
                success=False,
                message="配置文件不存在",
                error=f"找不到配置文件: {config_name}"
            )
        
        # 删除文件
        config_path.unlink()
        
        return APIResponse(
            success=True,
            message=f"配置文件 {config_name} 删除成功",
            data={"deleted_file": config_name}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


@router.post("/validate", response_model=APIResponse)
async def validate_configuration(request: ConfigValidationRequest):
    """验证配置数据的正确性"""
    try:
        # 尝试转换和验证配置数据
        try:
            if 'simulation' in request.config_data:
                # 已经是新格式
                config_model = SimulationConfigModel(**request.config_data)
            else:
                # 传统格式，需要转换
                config_model = convert_dict_to_yaml(request.config_data)
            
            # 额外的业务逻辑验证
            validation_warnings = []
            
            # 检查参数合理性
            if config_model.vehicles.count > 100:
                validation_warnings.append("车辆数量过多，可能影响性能")
            
            if config_model.simulation.duration > 7200:  # 2小时
                validation_warnings.append("仿真时长较长，建议使用较小的时间步长")
            
            if config_model.orders.generation_rate > 5000:
                validation_warnings.append("订单生成率过高，可能导致系统过载")
            
            return APIResponse(
                success=True,
                message="配置验证通过",
                data={
                    "valid": True,
                    "config": config_model.dict(),
                    "warnings": validation_warnings
                }
            )
            
        except ValidationError as e:
            validation_errors = []
            for error in e.errors():
                field_path = " -> ".join(str(x) for x in error["loc"])
                validation_errors.append({
                    "field": field_path,
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            return APIResponse(
                success=False,
                message="配置验证失败",
                data={
                    "valid": False,
                    "errors": validation_errors
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置验证失败: {str(e)}")


@router.get("/templates/list", response_model=APIResponse)
async def list_templates():
    """列出所有配置模板"""
    try:
        template_files = list(config_manager.templates_dir.glob("*.yaml"))
        templates_info = []
        
        for template_file in template_files:
            template_name = template_file.stem
            try:
                template = config_manager.load_template(template_name)
                info = {
                    "name": template_name,
                    "filename": template_file.name,
                    "simulation_name": template.simulation.name,
                    "location": template.simulation.location,
                    "vehicles": template.vehicles.count,
                    "duration": template.simulation.duration
                }
                templates_info.append(info)
            except Exception as e:
                templates_info.append({
                    "name": template_name,
                    "filename": template_file.name,
                    "error": str(e)
                })
        
        return APIResponse(
            success=True,
            message=f"找到 {len(templates_info)} 个模板",
            data={"templates": templates_info}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


@router.post("/templates/{template_name}", response_model=APIResponse)
async def create_template(template_name: str, request: ConfigValidationRequest):
    """创建配置模板"""
    try:
        # 转换和验证配置数据
        try:
            if 'simulation' in request.config_data:
                config_model = SimulationConfigModel(**request.config_data)
            else:
                config_model = convert_dict_to_yaml(request.config_data)
        except ValidationError as e:
            return APIResponse(
                success=False,
                message="配置数据验证失败",
                error=f"配置验证错误: {str(e)}"
            )
        
        # 创建模板
        success = config_manager.create_template(template_name, config_model)
        
        if success:
            return APIResponse(
                success=True,
                message=f"模板 {template_name} 创建成功",
                data={"template_name": template_name}
            )
        else:
            return APIResponse(
                success=False,
                message="创建模板失败",
                error="无法保存模板文件"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建模板失败: {str(e)}")


@router.get("/templates/{template_name}", response_model=APIResponse)
async def get_template(template_name: str):
    """获取指定的配置模板"""
    try:
        template = config_manager.load_template(template_name)
        
        return APIResponse(
            success=True,
            message=f"模板 {template_name} 加载成功",
            data={
                "template_name": template_name,
                "config": template.dict()
            }
        )
        
    except FileNotFoundError:
        return APIResponse(
            success=False,
            message="模板不存在",
            error=f"找不到模板: {template_name}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}") 