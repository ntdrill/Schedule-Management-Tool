from dataclasses import dataclass
from enum import Enum
import math
from typing import List, Optional

class DecayDynamics(Enum):
    """
    状態悪化の関数型定義
    """
    LINEAR = "Linear"         # 時間に対し線形に悪化 (埃の蓄積など)
    EXPONENTIAL = "Exponential" # 指数関数的に悪化 (カビ、腐敗など)
    SIGMOID = "Sigmoid"       # S字カーブ (ある程度までは耐えるが、限界を超えると急激に悪化し、飽和する)

class CostDynamics(Enum):
    """
    介入コストの関数型定義
    """
    LINEAR = "Linear"             # 状態値に比例してコストが増加 (Base + Unit * S)
    EXPONENTIAL = "Exponential"   # 状態悪化に伴いコストが指数的に増大 (Base + Unit * (e^(k*S) - 1))
    # 規模の経済は、Base(固定費)が大きくUnit(変動費)が小さいLINEARモデルで表現される

@dataclass
class EnvironmentStateVariable:
    """
    環境状態変数定義
    物理的特性と心理的重み付けを管理する
    """
    name: str
    description: str
    current_value: float = 0.0  # 0.0 (最良/秩序) -> 1.0 (最悪/無秩序) の正規化された値
    
    # Entropic Physics Parameters
    entropy_weight: float = 1.0       # 心理的・機能的影響度 (0.0-1.0)
    decay_dynamics: DecayDynamics = DecayDynamics.LINEAR
    rate_coefficient: float = 0.1     # 崩壊速度係数 (値が大きいほど早く悪化)
    
    # Cost Parameters (Intervention)
    cost_dynamics: CostDynamics = CostDynamics.LINEAR
    base_intervention_cost: float = 10.0  # 介入の固定コスト（準備、移動、精神的ハードル）
    unit_intervention_cost: float = 5.0   # 介入の変動コスト係数（汚れの量に応じた手間）
    
    def predict_value(self, time_delta: float) -> float:
        """
        指定時間経過後の状態値を予測する (MPC用)
        """
        future_val = self.current_value
        
        if self.decay_dynamics == DecayDynamics.LINEAR:
            future_val += self.rate_coefficient * time_delta
            
        elif self.decay_dynamics == DecayDynamics.EXPONENTIAL:
            epsilon = 0.01
            future_val = (self.current_value + epsilon) * math.exp(self.rate_coefficient * time_delta) - epsilon

        elif self.decay_dynamics == DecayDynamics.SIGMOID:
            if self.current_value <= 0.001:
                logit = -6.0
            elif self.current_value >= 0.999:
                logit = 6.0
            else:
                logit = math.log(self.current_value / (1.0 - self.current_value))
            
            logit += self.rate_coefficient * time_delta
            future_val = 1.0 / (1.0 + math.exp(-logit))

        return min(max(future_val, 0.0), 1.0)

    def calculate_weighted_entropy(self, projected_value: Optional[float] = None) -> float:
        """
        現在の(または予測された)物理的エントロピーに対する、重み付き評価値を計算
        E = S * w
        """
        val = projected_value if projected_value is not None else self.current_value
        return val * self.entropy_weight

    def calculate_intervention_cost(self, projected_value: Optional[float] = None) -> float:
        """
        その時点での状態を0(完全回復)に戻すために必要なコストを計算
        Cost = Base + VariableCost(S)
        """
        val = projected_value if projected_value is not None else self.current_value
        
        cost = self.base_intervention_cost
        
        if self.cost_dynamics == CostDynamics.LINEAR:
            cost += self.unit_intervention_cost * val
            
        elif self.cost_dynamics == CostDynamics.EXPONENTIAL:
            # 状態1.0でコストが跳ね上がるように調整
            # 例: Unit * (e^(3*S) - 1)  S=1でe^3(約20)倍
            # ここではシンプルに係数のみで制御できるよう Unit * S は使わず
            # Unit * (e^(coeff * S) - 1) の形が望ましいが、
            # パラメータ削減のため、単純な指数関数モデルとする:
            # Cost += Unit * (exp(4 * val) - 1) / (exp(4) - 1) -> 0-1正規化?
            # いや、Iveの言う「跳ね上がる」を表現するには、Unit自体が大きな係数であればよい。
            # S=0 -> Cost = Base
            # S=1 -> Cost = Base + Unit * (e - 1) ? 少し弱いか。
            # ここではモデルを「Unit * (e^(5*S) - 1)」として、S=1のときUnitの約148倍になるようにする
            cost += self.unit_intervention_cost * (math.exp(5.0 * val) - 1.0) * 0.01 # 0.01はスケーリング用

        return cost

# 具体的な定義マスタ
DEFAULT_ENVIRONMENT_VARIABLES = [
    EnvironmentStateVariable(
        name="DustAccumulation",
        description="床や棚の埃の蓄積",
        entropy_weight=0.4,
        decay_dynamics=DecayDynamics.LINEAR,
        rate_coefficient=0.05, 
        # 規模の経済: 固定コストが高く、変動コストは低い
        cost_dynamics=CostDynamics.LINEAR,
        base_intervention_cost=8.0,  # 掃除機を出すのが面倒
        unit_intervention_cost=2.0   # 吸う時間は汚れが増えてもそこまで変わらない
    ),
    EnvironmentStateVariable(
        name="MoldRisk",
        description="水回りのカビ発生リスク",
        entropy_weight=0.9,
        decay_dynamics=DecayDynamics.EXPONENTIAL,
        rate_coefficient=0.15,
        # 放置の代償: 悪化するとコストが激増
        cost_dynamics=CostDynamics.EXPONENTIAL,
        base_intervention_cost=2.0,   # 最初は拭くだけ
        unit_intervention_cost=100.0  # 酷くなるとカビキラー漬け置き＋ブラッシング（非常に高コスト）
    ),
    EnvironmentStateVariable(
        name="AirQuality",
        description="CO2濃度および換気状態",
        entropy_weight=0.7,
        decay_dynamics=DecayDynamics.SIGMOID,
        rate_coefficient=0.8,
        # 換気に規模の経済はない（一定）
        cost_dynamics=CostDynamics.LINEAR,
        base_intervention_cost=2.0,  # 窓を開けるだけ
        unit_intervention_cost=0.0   # どれだけ汚れていても開ける手間は同じ
    ),
    EnvironmentStateVariable(
        name="Clutter",
        description="整理整頓（散らかり具合）",
        entropy_weight=0.6,
        decay_dynamics=DecayDynamics.LINEAR,
        rate_coefficient=0.1,
        # 片付けは量に比例して時間がかかる
        cost_dynamics=CostDynamics.LINEAR,
        base_intervention_cost=5.0,  #「さあやるぞ」という気合
        unit_intervention_cost=15.0  # 物の量に比例して大変
    )
]
