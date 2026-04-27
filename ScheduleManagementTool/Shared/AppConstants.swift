import Foundation

enum AppConstants {
    // --- v1 必須定数 ---
    static let measurementLimitDailyMaxMinutes: Double = 480.0
    static let switchBotPollingIntervalSeconds: TimeInterval = 60.0

    // --- v1 プレースホルダー定数 ---
    static let measurementQualityThreshold: Double = 0.5
    static let environmentRecoveryMinThreshold: Double = 0.6
    static let measurementRestartMinStabilitySeconds: Double = 300.0
    static let thresholdMeasurementCapabilityForMonitoring: Double = 0.4
    static let thresholdDiscrepancyForDissociationAlert: Double = 2.0

    // --- 期待状態プリセット初期シード ---
    static let defaultActionTemplates: [ActionTemplate] = [
        ActionTemplate(id: "deep_breathing", name: "深呼吸", category: "呼吸法", estimatedDurationSeconds: 180, displayOrder: 0),
        ActionTemplate(id: "pulse_shift", name: "パルスシフト", category: "運動", estimatedDurationSeconds: 300, displayOrder: 1),
        ActionTemplate(id: "stretching", name: "ストレッチ", category: "運動", estimatedDurationSeconds: 300, displayOrder: 2),
        ActionTemplate(id: "hydration", name: "水分補給", category: "摂取", estimatedDurationSeconds: 60, displayOrder: 3),
        ActionTemplate(id: "short_walk", name: "短い散歩", category: "運動", estimatedDurationSeconds: 600, displayOrder: 4),
    ]
}
