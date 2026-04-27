import Foundation

struct UserStateHistoryRecordDTO: Codable, Sendable {
    var id: UUID
    var timestamp: Date
    var heartRateBpm: Double?
    var hrvMs: Double?
    var valenceScore: Double?
    var arousalScore: Double?
    var focusScore: Double?
    var fatigueScore: Double?
    var temperature: Double?
    var humidity: Double?
    var expectedStateId: String?
    var isMeasurementActive: Bool
    var recordTypeRaw: String
}
