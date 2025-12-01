from environment_dynamics import DEFAULT_ENVIRONMENT_VARIABLES, DecayDynamics
import matplotlib.pyplot as plt

def run_simulation(duration=50, step=1):
    print(f"{'Time':<5} | {'Name':<15} | {'Value':<10} | {'Weighted Entropy':<15}")
    print("-" * 55)

    # 各変数の時系列データを保存するための辞書
    history = {var.name: [] for var in DEFAULT_ENVIRONMENT_VARIABLES}
    time_points = range(0, duration + 1, step)

    for t in time_points:
        print(f"t={t:<3}")
        for var in DEFAULT_ENVIRONMENT_VARIABLES:
            # 予測値を計算
            pred_val = var.predict_value(time_delta=float(t))
            weighted_entropy = var.calculate_weighted_entropy(pred_val)
            
            history[var.name].append(pred_val)
            
            print(f"{'':<5} | {var.name:<15} | {pred_val:.4f}     | {weighted_entropy:.4f}")
        print("-" * 20)

    return time_points, history

if __name__ == "__main__":
    run_simulation()

