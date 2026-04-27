import Foundation

struct SensorSnapshot: Codable, Equatable, Sendable {
    var heartRateBpm: Double?
    var hrvMs: Double?
    var temperature: Double?
    var humidity: Double?
    var capturedAt: Date

    init(heartRateBpm: Double? = nil, hrvMs: Double? = nil,
         temperature: Double? = nil, humidity: Double? = nil,
         capturedAt: Date = Date()) {
        self.heartRateBpm = heartRateBpm
        self.hrvMs = hrvMs
        self.temperature = temperature
        self.humidity = humidity
        self.capturedAt = capturedAt
    }
}
