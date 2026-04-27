import Foundation

struct DeltaResult: Codable, Equatable, Sendable {
    var valenceChange: Double?
    var arousalChange: Double?
    var focusChange: Double?
    var fatigueChange: Double?
    var heartRateChange: Double?
    var hrvChange: Double?
    var overallChangeScore: Double?

    init() {}
}
