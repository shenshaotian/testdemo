import yaml
import json
import os
from typing import Dict, Any, List


class DataLoader:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), '..', 'test_data')

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """加载YAML文件"""
        file_path = os.path.join(self.base_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"测试数据文件未找到: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML文件格式错误: {e}")

    def load_json(self, filename: str) -> Dict[str, Any]:
        """加载JSON文件（备用）"""
        file_path = os.path.join(self.base_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"测试数据文件未找到: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件格式错误: {e}")

    def get_test_data(self, data_key: str, filename: str = 'products.yaml') -> Any:
        """获取特定的测试数据"""
        if filename.endswith('.json'):
            data = self.load_json(filename)
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            data = self.load_yaml(filename)
        else:
            # 默认尝试YAML，如果失败尝试JSON
            try:
                data = self.load_yaml(filename)
            except:
                data = self.load_json(filename)

        return data.get(data_key, {})

    def get_test_cases(self, filename: str = 'products.yaml') -> List[Dict]:
        """获取测试用例数据"""
        data = self.get_test_data('test_cases', filename)
        return data if isinstance(data, list) else []

    def update_test_data(self, data_key: str, new_data: Any, filename: str = 'products.yaml'):
        """更新测试数据"""
        file_path = os.path.join(self.base_path, filename)

        # 读取现有数据
        if filename.endswith('.json'):
            all_data = self.load_json(filename)
        else:
            all_data = self.load_yaml(filename)

        # 更新数据
        all_data[data_key] = new_data

        # 写回文件
        if filename.endswith('.json'):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(all_data, f, allow_unicode=True, default_flow_style=False)


# 创建全局实例
test_data_loader = DataLoader()