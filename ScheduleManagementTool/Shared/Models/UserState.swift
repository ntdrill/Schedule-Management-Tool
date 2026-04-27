import Foundation
import SwiftData

@Model
final class UserState {
    var id: UUID = UUID()
    var timestamp: Date = Date()

    // --- センサーデータ ---
    var heartRateBpm: Double?
    var hrvMs: Double?

    // --- 主観入力 [1-5] ---
    var valenceScore: Double?
    var arousalScore: Double?
    var focusScore: Double?
    var fatigueScore: Double?

    // --- 測定状態フラグ ---
    var isMeasurementStateActive: Bool = false

    // --- 期待状態（プリセット選択） ---
    var expectedStateId: String?

    // --- v1 骨格フィールド ---
    var measurementCapability: Double?
    var measurementCapabilityStatusRaw: String = "normal"

    // --- Relationship ---
    @Relationship(deleteRule: .cascade, inverse: \UserStateHistoryRecord.userState)
    var historyRecords: [UserStateHistoryRecord] = []

    init() {}
}
