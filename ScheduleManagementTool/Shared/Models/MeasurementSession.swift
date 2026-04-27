import Foundation
import SwiftData

@Model
final class MeasurementSession {
    var id: UUID = UUID()
    var startTimestamp: Date = Date()
    var endTimestamp: Date?
    var statusRaw: String = "active"

    // --- 測定時間管理 ---
    var measurementTimeDailyMinutes: Double = 0.0
    var lastValidMeasurementTimestamp: Date?

    // --- v1 骨格フィールド ---
    var measurementQualityScore: Double?
    var measurementFatigueLevel: Double?
    var isMeasurementMode: Bool = true

    // --- Relationship ---
    @Relationship(deleteRule: .cascade, inverse: \ExecutionRecord.measurementSession)
    var executionRecords: [ExecutionRecord] = []

    @Relationship(deleteRule: .cascade, inverse: \UserStateHistoryRecord.measurementSession)
    var stateRecords: [UserStateHistoryRecord] = []

    init() {}
}
