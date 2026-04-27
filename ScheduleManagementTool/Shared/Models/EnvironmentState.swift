import Foundation
import SwiftData

@Model
final class EnvironmentState {
    var id: UUID = UUID()
    var timestamp: Date = Date()

    var temperature: Double?
    var humidity: Double?

    init() {}
}
