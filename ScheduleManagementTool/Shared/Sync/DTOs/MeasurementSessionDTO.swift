import Foundation

struct MeasurementSessionDTO: Codable, Sendable {
    var id: UUID
    var startTimestamp: Date
    var endTimestamp: Date?
    var statusRaw: String
    var measurementTimeDailyMinutes: Double
    var lastValidMeasurementTimestamp: Date?
    var measurementQualityScore: Double?
    var measurementFatigueLevel: Double?
    var isMeasurementMode: Bool
}
