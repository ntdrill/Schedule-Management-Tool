from environment_dynamics import DEFAULT_ENVIRONMENT_VARIABLES, EnvironmentStateVariable
import matplotlib.pyplot as plt
import copy

def calculate_total_cost(variable: EnvironmentStateVariable, intervention_threshold: float, duration: int = 100):
    """
    指定された介入閾値で運用した場合の総コスト(J)を計算する
    J = Σ(Penalty(S(t)) + InterventionCost(Action(t)))
    """
    # シミュレーション用にオブジェクトを複製
    sim_var = copy.deepcopy(variable)
    sim_var.current_value = 0.0 # 初期状態はクリーンとする
    
    total_penalty = 0.0
    total_intervention_cost = 0.0
    intervention_count = 0
    
    history_value = []
    
    for t in range(duration):
        # 1. 現在の状態に対するペナルティを加算 (Penalty = Weighted Entropy)
        current_penalty = sim_var.calculate_weighted_entropy()
        total_penalty += current_penalty
        history_value.append(sim_var.current_value)
        
        # 2. 介入判定
        if sim_var.current_value >= intervention_threshold:
            # 介入実行
            cost = sim_var.calculate_intervention_cost()
            total_intervention_cost += cost
            intervention_count += 1
            
            # 状態リセット (完全回復とする)
            sim_var.current_value = 0.0
        else:
            # 3. 状態遷移 (介入しなかった場合のみ悪化)
            # predict_valueは引数がtime_deltaなので、1ステップ分(1.0)進める
            # ただしpredict_valueは「現在の値からの予測」を返すので、current_valueを更新する
            sim_var.current_value = sim_var.predict_value(1.0)
            
    total_cost = total_penalty + total_intervention_cost
    return total_cost, intervention_count, total_penalty, total_intervention_cost

def run_optimization_simulation():
    print(f"{'Variable':<15} | {'Threshold':<10} | {'Total Cost':<10} | {'Penalty':<10} | {'Action Cost':<10} | {'Count':<5}")
    print("-" * 75)

    results = {}

    for var in DEFAULT_ENVIRONMENT_VARIABLES:
        best_threshold = 0.0
        min_total_cost = float('inf')
        best_details = None
        
        # 閾値を 0.1 から 1.0 まで 0.05 刻みで探索
        thresholds = [round(x * 0.05, 2) for x in range(2, 21)] # 0.10 - 1.00
        
        print(f"--- {var.name} ---")
        
        for th in thresholds:
            total, count, penalty, action = calculate_total_cost(var, th, duration=200)
            
            # 最適値の更新
            if total < min_total_cost:
                min_total_cost = total
                best_threshold = th
                best_details = (total, penalty, action, count)
                
            # 詳細ログ(デバッグ用、間引いて表示)
            if th in [0.2, 0.5, 0.8, 1.0]:
                print(f"{'':<15} | {th:<10.2f} | {total:<10.1f} | {penalty:<10.1f} | {action:<10.1f} | {count:<5}")

        print(f"OPTIMAL STRATEGY for {var.name}: Threshold = {best_threshold}")
        print(f"  Min Cost: {min_total_cost:.1f} (Penalty: {best_details[1]:.1f}, Action: {best_details[2]:.1f}, Count: {best_details[3]})")
        print("")
        
        results[var.name] = best_threshold

if __name__ == "__main__":
    run_optimization_simulation()

