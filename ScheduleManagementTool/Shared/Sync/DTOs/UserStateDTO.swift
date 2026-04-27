import Foundation

struct UserStateDTO: Codable, Sendable {
    var id: UUID
    var timestamp: Date
    var heartRateBpm: Double?
    var hrvMs: Double?
    var valenceScore: Double?
    var arousalScore: Double?
    var focusScore: Double?
    var fatigueScore: Double?
    var isMeasurementStateActive: Bool
    var measurementCapability: Double?
    var measurementCapabilityStatusRaw: String
}
