from dataclasses import dataclass
from typing import List, Dict, Tuple
import copy
from environment_dynamics import EnvironmentStateVariable, DEFAULT_ENVIRONMENT_VARIABLES

@dataclass
class UserResource:
    """
    ユーザーの保有リソース定義
    """
    time_available: float   # 分単位あるいは任意の時間単位
    energy_available: float # ユーザーの体力/気力 (0-100等の任意単位)

@dataclass
class TaskRequest:
    """
    各状態変数からの介入リクエスト
    """
    variable_name: str
    required_time: float
    required_energy: float
    current_penalty: float # 現時点でのペナルティ
    future_penalty_if_ignored: float # 無視した場合の次のタイムステップでのペナルティ予測
    
    @property
    def marginal_utility(self) -> float:
        """
        限界効用（機会費用）
        今やらなかった場合に増えるペナルティの量 = 介入の価値
        """
        return self.future_penalty_if_ignored - self.current_penalty
    
    @property
    def roi(self) -> float:
        """
        投資対効果 (Return On Investment)
        単位コストあたりの被害防止量
        ここではシンプルに時間効率とエネルギー効率の調和平均や重み付けが可能だが、
        一旦「損失回避量 / (時間 + エネルギー)」の簡易モデルとする
        """
        cost_metric = self.required_time + self.required_energy
        if cost_metric <= 0: return float('inf')
        return (self.future_penalty_if_ignored - self.current_penalty) / cost_metric

class ResourceArbitrator:
    """
    リソース調停レイヤー
    """
    def __init__(self, variables: List[EnvironmentStateVariable]):
        self.variables = variables

    def generate_requests(self, time_horizon: float = 1.0) -> List[TaskRequest]:
        """
        現在の全変数から介入リクエストを生成する
        """
        requests = []
        for var in self.variables:
            # 現時点での状態
            current_val = var.current_value
            current_penalty = var.calculate_weighted_entropy(current_val)
            
            # 放置した場合の未来の状態
            future_val = var.predict_value(time_horizon)
            future_penalty = var.calculate_weighted_entropy(future_val)
            
            # コスト計算 (単純化のため、状態変数定義から取得するロジックを想定)
            # 実際の介入コストは状態値に依存する場合があるが、
            # ここではEnvironmentStateVariableに定義されたcalculate_intervention_costを使用
            cost = var.calculate_intervention_cost(current_val)
            
            # 時間コスト等は現状モデルに含まれていないため、intervention_costを
            # エネルギーと時間の複合として仮定する、あるいは別途定義が必要だが
            # ここでは一旦 cost を両方のリソース消費として扱う簡易実装
            
            requests.append(TaskRequest(
                variable_name=var.name,
                required_time=cost * 0.5, # 仮: コストの半分が時間
                required_energy=cost * 0.5, # 仮: コストの半分が体力
                current_penalty=current_penalty,
                future_penalty_if_ignored=future_penalty
            ))
        return requests

    def arbitrate(self, resources: UserResource, requests: List[TaskRequest]) -> Tuple[List[TaskRequest], List[TaskRequest]]:
        """
        ナップサック問題的アプローチでタスクを選択する
        
        Args:
            resources: ユーザーの空きリソース
            requests: 介入候補リスト
            
        Returns:
            accepted: 実行するタスク
            rejected: 却下（先送り）するタスク
        """
        # 限界効用（機会費用）が高い順、あるいはROIが高い順にソート
        # ここでは「今やらないとどれだけ損するか」という機会費用を重視する戦略をとる
        # つまり、微分値（悪化速度）が大きいものを優先
        sorted_requests = sorted(requests, key=lambda x: x.marginal_utility, reverse=True)
        
        accepted = []
        rejected = []
        
        current_time = 0.0
        current_energy = 0.0
        
        for req in sorted_requests:
            # リソース制約チェック
            if (current_time + req.required_time <= resources.time_available) and \
               (current_energy + req.required_energy <= resources.energy_available):
                
                accepted.append(req)
                current_time += req.required_time
                current_energy += req.required_energy
            else:
                rejected.append(req)
                
        return accepted, rejected

# シミュレーション用ヘルパー
def simulate_arbitration():
    # 変数初期化 (あえて悪い状態を作って競合させる)
    vars_snapshot = copy.deepcopy(DEFAULT_ENVIRONMENT_VARIABLES)
    
    # MoldRisk: 臨界点手前 (放置するとヤバい)
    vars_snapshot[1].current_value = 0.7 
    
    # AirQuality: 既に悪い (放置してもこれ以上悪くならないかも？いや、Saturationする)
    vars_snapshot[2].current_value = 0.9
    
    # Dust: 普通に溜まっている
    vars_snapshot[0].current_value = 0.5
    
    # Clutter: 溜まっている
    vars_snapshot[3].current_value = 0.6

    arbitrator = ResourceArbitrator(vars_snapshot)
    requests = arbitrator.generate_requests(time_horizon=1.0) # 1tick放置した場合の差分を見る

    print("--- Task Requests (Opportunity Cost Analysis) ---")
    print(f"{'Name':<15} | {'Cur P':<6} | {'Fut P':<6} | {'Diff (Loss)':<11} | {'Cost(T/E)':<10}")
    print("-" * 60)
    for r in requests:
        loss = r.future_penalty_if_ignored - r.current_penalty
        print(f"{r.variable_name:<15} | {r.current_penalty:.2f}   | {r.future_penalty_if_ignored:.2f}   | {loss:+.4f}      | {r.required_time:.1f}/{r.required_energy:.1f}")
    print("")

    # ケース1: 余裕がある場合
    print("--- Case 1: Rich Resources (Time=100, Energy=100) ---")
    res1 = UserResource(time_available=100, energy_available=100)
    acc1, rej1 = arbitrator.arbitrate(res1, requests)
    print(f"Accepted: {[r.variable_name for r in acc1]}")
    print(f"Rejected: {[r.variable_name for r in rej1]}")
    print("")

    # ケース2: 逼迫している場合
    print("--- Case 2: Scarse Resources (Time=20, Energy=20) ---")
    res2 = UserResource(time_available=20, energy_available=20)
    acc2, rej2 = arbitrator.arbitrate(res2, requests)
    print(f"Accepted: {[r.variable_name for r in acc2]}")
    print(f"Rejected: {[r.variable_name for r in rej2]}")
    
if __name__ == "__main__":
    simulate_arbitration()

