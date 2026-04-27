import Foundation
import SwiftData

@Model
final class ActualStateSnapshot {
    var id: UUID = UUID()
    var timestamp: Date = Date()

    var heartRateBpm: Double?
    var hrvMs: Double?

    var valenceScore: Double?
    var arousalScore: Double?
    var focusScore: Double?
    var fatigueScore: Double?

    var temperature: Double?
    var humidity: Double?

    var sourceDescription: String?

    init() {}
}
