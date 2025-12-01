from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from environment_dynamics import EnvironmentStateVariable, DecayDynamics
from arbitration_layer import TaskRequest, UserResource

class RejectionReason(Enum):
    RESOURCE_SHORTAGE = "ResourceShortage" # 時間・体力が足りない
    LOW_ROI = "LowROI"                     # 今やるメリットが薄い（まだ溜まっていない）
    DEPRIORITIZED = "Deprioritized"        # 他により重要なタスクがある
    NOT_APPLICABLE = "NotApplicable"       # そもそも介入不要

@dataclass
class ProjectedCostPoint:
    """
    未来のコスト予測点（グラフ描画用）
    """
    time_offset: int       # 現在からの経過時間 (e.g., 1, 2, 3...)
    predicted_penalty: float # その時点での放置ペナルティ
    predicted_action_cost: float # その時点で介入した場合のコスト

@dataclass
class PersuasiveTaskData:
    """
    UI向けの説得メタデータ付きタスクオブジェクト
    """
    # 基本情報
    task_id: str
    title: str
    description: str
    
    # 実行コスト
    required_time: float
    required_energy: float
    
    # 説得用指標
    urgency_score: float # 0.0-1.0: 視覚的な緊急度（赤色表示など）
    roi_value: float     # 投資対効果（今やるとどれだけ得か）
    
    # 未来コスト投影 (チャート用データ)
    projected_cost_series: List[ProjectedCostPoint]
    
    # テキストによる説得メッセージ
    persuasion_message: str # 例: "今やれば5分ですが、来週は3時間かかります"

@dataclass
class RejectedTaskData:
    """
    却下されたタスクの情報（ユーザーの罪悪感軽減用）
    """
    task_id: str
    title: str
    reason: RejectionReason
    justification_message: str # 例: "まだ掃除するほど汚れていません。来週末まで待ちましょう。"

class PersuasiveAdapter:
    """
    Simulation/Arbitrationの結果をUI向けデータに変換するアダプター
    """
    
    def generate_presentation_data(self, 
                                 accepted_requests: List[TaskRequest], 
                                 rejected_requests: List[TaskRequest],
                                 variables_map: Dict[str, EnvironmentStateVariable],
                                 projection_horizon: int = 10) -> Dict[str, List]:
        
        presentation_data = {
            "suggested_tasks": [],
            "postponed_tasks": []
        }
        
        # 1. 採用タスクの変換
        for req in accepted_requests:
            var = variables_map[req.variable_name]
            
            # 未来投影データの生成
            series = []
            # 現時点(0)からhorizonまで
            # シミュレーションのための一時オブジェクト
            sim_var = var # ここでは簡易的に参照するが、厳密にはcopyが必要
            # しかしpredict_valueは純粋関数に近いので、現在値から毎回計算する
            
            # メッセージ生成ロジック
            message = ""
            if var.decay_dynamics == DecayDynamics.EXPONENTIAL:
                message = f"警告: {var.name}のリスクが指数関数的に増大しています。今対処するのが最も低コストです。"
            elif var.decay_dynamics == DecayDynamics.SIGMOID:
                message = f"注意: {var.name}が悪化する瀬戸際です。これ以上放置すると環境が急変します。"
            else: # Linear
                message = f"そろそろ{var.name}の対処時期です。溜まった汚れを一掃しましょう。"

            # プロジェクション計算
            # 現在の状態を起点に、t=0, t=1... t=horizon までのコストを計算
            current_val_base = var.current_value
            
            for t in range(projection_horizon + 1):
                # t時点での予測値
                pred_val = var.predict_value(float(t))
                
                # その時点でのペナルティと介入コスト
                # 注意: EnvironmentStateVariableのメソッドは「現在のcurrent_value」を使う設計になっているため
                # 一時的に値をセットするか、計算ロジックを分離する必要がある。
                # ここではロジック再利用のため、計算メソッドに引数を渡せるように前のステップで修正済みと仮定、
                # もしくは predict_value の戻り値を使って計算する。
                # optimization_simulation.py では calculate_intervention_cost(projected_value) を実装した。
                
                p_cost = var.calculate_intervention_cost(pred_val)
                penalty = var.calculate_weighted_entropy(pred_val)
                
                series.append(ProjectedCostPoint(
                    time_offset=t,
                    predicted_penalty=penalty,
                    predicted_action_cost=p_cost
                ))

            task_data = PersuasiveTaskData(
                task_id=f"task_{req.variable_name}",
                title=f"{var.name}への介入",
                description=var.description,
                required_time=req.required_time,
                required_energy=req.required_energy,
                urgency_score=min(req.marginal_utility * 10.0, 1.0), # 簡易スケーリング
                roi_value=req.roi,
                projected_cost_series=series,
                persuasion_message=message
            )
            presentation_data["suggested_tasks"].append(task_data)

        # 2. 却下タスクの変換
        for req in rejected_requests:
            var = variables_map[req.variable_name]
            
            # 理由の推定 (簡易ロジック)
            reason = RejectionReason.RESOURCE_SHORTAGE # デフォルト
            justification = "今はリソース（時間・体力）が不足しています。優先度の高いタスクに集中しましょう。"
            
            # もしROIが極端に低いなら、まだ時期尚早
            if req.marginal_utility < 0.01 and var.decay_dynamics == DecayDynamics.LINEAR:
                reason = RejectionReason.LOW_ROI
                justification = "まだ介入効果が低いため、効率的ではありません。もう少し溜めてから処理します。"
            
            rejected_data = RejectedTaskData(
                task_id=f"rej_{req.variable_name}",
                title=f"{var.name} (延期)",
                reason=reason,
                justification_message=justification
            )
            presentation_data["postponed_tasks"].append(rejected_data)
            
        return presentation_data

