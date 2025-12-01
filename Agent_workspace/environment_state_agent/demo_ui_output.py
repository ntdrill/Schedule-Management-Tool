import json
from dataclasses import asdict
from environment_dynamics import DEFAULT_ENVIRONMENT_VARIABLES
from arbitration_layer import ResourceArbitrator, UserResource
from persuasive_adapter import PersuasiveAdapter
import copy

def run_persuasion_demo():
    # 1. 環境セットアップ (Arbitration Layerのシミュレーションと同じ状況)
    vars_map = {v.name: v for v in DEFAULT_ENVIRONMENT_VARIABLES}
    
    # シミュレーション用スナップショット
    current_vars = copy.deepcopy(DEFAULT_ENVIRONMENT_VARIABLES)
    # 状態設定: Moldは危険、Airは悪い、Dust/Clutterはそこそこ
    for v in current_vars:
        if v.name == "MoldRisk": v.current_value = 0.7
        elif v.name == "AirQuality": v.current_value = 0.9
        elif v.name == "DustAccumulation": v.current_value = 0.5
        elif v.name == "Clutter": v.current_value = 0.6
        
    sim_vars_map = {v.name: v for v in current_vars}

    # 2. 調停実行 (リソース不足シナリオ)
    arbitrator = ResourceArbitrator(current_vars)
    requests = arbitrator.generate_requests(time_horizon=1.0)
    
    resources = UserResource(time_available=20, energy_available=20)
    accepted, rejected = arbitrator.arbitrate(resources, requests)

    # 3. アダプターによる変換
    adapter = PersuasiveAdapter()
    ui_data = adapter.generate_presentation_data(accepted, rejected, sim_vars_map, projection_horizon=5)

    # 4. JSON出力 (UIが受け取るデータ形式)
    # dataclassをdictに変換、Enumを文字列に変換するヘルパー
    def json_serializer(obj):
        if hasattr(obj, 'value'): # Enum
            return obj.value
        raise TypeError(f"Type {type(obj)} not serializable")

    output = {
        "suggested_tasks": [asdict(t) for t in ui_data["suggested_tasks"]],
        "postponed_tasks": [asdict(t) for t in ui_data["postponed_tasks"]]
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False, default=json_serializer))

if __name__ == "__main__":
    run_persuasion_demo()

