import Foundation
import SwiftData

@Model
final class UserStateHistoryRecord {
    var id: UUID = UUID()
    var timestamp: Date = Date()

    // --- センサースナップショット ---
    var heartRateBpm: Double?
    var hrvMs: Double?

    // --- 主観スナップショット ---
    var valenceScore: Double?
    var arousalScore: Double?
    var focusScore: Double?
    var fatigueScore: Double?

    // --- 環境スナップショット（v1骨格: 温度・湿度のみ）---
    var temperature: Double?
    var humidity: Double?

    // --- 期待状態参照 ---
    var expectedStateId: String?

    // --- コンテキスト ---
    var isMeasurementActive: Bool = false
    var recordTypeRaw: String = "periodic"

    // --- Relationship ---
    var userState: UserState?
    var measurementSession: MeasurementSession?

    init() {}
}
