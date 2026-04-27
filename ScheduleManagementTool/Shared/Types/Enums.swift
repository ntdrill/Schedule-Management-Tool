import Foundation

enum MeasurementSessionStatus: String, Codable, Sendable {
    case idle = "idle"
    case active = "active"
    case completed = "completed"
    case cancelled = "cancelled"
}

enum ExpectedStatePreset: String, Codable, CaseIterable, Sendable {
    case standard = "standard"
    case ready = "ready"
    case focus = "focus"
    case rest = "rest"
    case sleep = "sleep"
}

enum MeasurementCapabilityStatus: String, Codable, Sendable {
    case normal = "normal"
    case degraded = "degraded"
    case recoveryPending = "recoveryPending"
    case unavailable = "unavailable"
}

enum MeasurementSessionQuality: String, Codable, Sendable {
    case high = "high"
    case normal = "normal"
    case low = "low"
}
