import json
import sys
from typing import List, Dict

def draw_ascii_chart(series: List[Dict], max_height: int = 10, width: int = 30):
    """
    projected_cost_series からアスキーアートのグラフを描画する
    """
    if not series:
        return ""

    # データ抽出
    values = [point['predicted_action_cost'] for point in series]
    max_val = max(values)
    min_val = 0 # コストなので0起点
    
    if max_val == 0:
        return "No cost data"

    # 正規化してグラフ化
    lines = []
    for h in range(max_height, -1, -1):
        threshold = (h / max_height) * max_val
        line = f"{threshold:>6.1f} | "
        
        for v in values:
            char = " "
            if v >= threshold:
                if v > threshold + (max_val/max_height)*0.5:
                    char = "*" # 完全に超えている
                else:
                    char = "." # ギリギリ
            line += f" {char} "
        lines.append(line)
    
    # X軸
    lines.append("       " + "-" * (len(values) * 3 + 2))
    lines.append("Time   " + "".join([f" {i:<2}" for i in range(len(values))]))
    
    return "\n".join(lines)

def render_task_card(task: Dict):
    print("=" * 60)
    print(f"🔥 TASK: {task['title']} (Urgency: {task['urgency_score']:.2f})")
    print("-" * 60)
    print(f"MESSAGE: {task['persuasion_message']}")
    print(f"COST: {task['required_time']:.1f} min / {task['required_energy']:.1f} energy")
    print(f"ROI: {task['roi_value']:.4f}")
    print("")
    print("FUTURE COST PROJECTION (If ignored):")
    print(draw_ascii_chart(task['projected_cost_series']))
    print("=" * 60)
    print("")

def render_postponed(tasks: List[Dict]):
    if not tasks: return
    print("\n" + "-" * 60)
    print(f"💤 POSTPONED TASKS ({len(tasks)})")
    print("-" * 60)
    for t in tasks:
        print(f"* {t['title']}")
        print(f"  Reason: {t['reason']}")
        print(f"  Note: {t['justification_message']}")
        print("")

def main():
    # 標準入力またはファイルからJSONを読み込む想定だが
    # ここではデモ用に demo_ui_output.py の出力をパイプされるか、
    # 直接実行してデモデータを生成する。
    
    # 簡易的に demo_ui_output.py をインポートしてデータ生成
    try:
        from demo_ui_output import run_persuasion_demo
        # 標準出力をキャプチャするのは面倒なので、demo_ui_outputの構造を少し変えるか
        # あるいはここで再シミュレーションする。
        # import済みモジュールを使ってデータ再生成
        from environment_dynamics import DEFAULT_ENVIRONMENT_VARIABLES
        from arbitration_layer import ResourceArbitrator, UserResource
        from persuasive_adapter import PersuasiveAdapter
        from dataclasses import asdict
        import copy
        
        # 1. データ生成 (demo_ui_output.py と同じロジック)
        vars_map = {v.name: v for v in DEFAULT_ENVIRONMENT_VARIABLES}
        current_vars = copy.deepcopy(DEFAULT_ENVIRONMENT_VARIABLES)
        for v in current_vars:
            if v.name == "MoldRisk": v.current_value = 0.7
            elif v.name == "AirQuality": v.current_value = 0.9
            elif v.name == "DustAccumulation": v.current_value = 0.5
            elif v.name == "Clutter": v.current_value = 0.6
            
        sim_vars_map = {v.name: v for v in current_vars}
        arbitrator = ResourceArbitrator(current_vars)
        requests = arbitrator.generate_requests(time_horizon=1.0)
        resources = UserResource(time_available=20, energy_available=20)
        accepted, rejected = arbitrator.arbitrate(resources, requests)
        adapter = PersuasiveAdapter()
        ui_data = adapter.generate_presentation_data(accepted, rejected, sim_vars_map, projection_horizon=5)
        
        # json serialize用の変換
        data = {
            "suggested_tasks": [asdict(t) for t in ui_data["suggested_tasks"]],
            "postponed_tasks": [asdict(t) for t in ui_data["postponed_tasks"]]
        }

    except ImportError:
        print("Error: Required modules not found.")
        return

    # レンダリング実行
    print("\n\n")
    print(">>> AGENT ADAM PERSUASIVE INTERFACE CLI v0.1 <<<")
    print("\n")
    
    for task in data["suggested_tasks"]:
        render_task_card(task)
        
    render_postponed(data["postponed_tasks"])

if __name__ == "__main__":
    main()

