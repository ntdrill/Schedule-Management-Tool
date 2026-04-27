import Foundation
import SwiftData

@Model
final class DeviceConnectionStatusMap {
    var id: UUID = UUID()
    var lastUpdated: Date = Date()
    var statusJson: String = "{}"

    init() {}
}
