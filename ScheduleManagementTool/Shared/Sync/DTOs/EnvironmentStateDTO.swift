import Foundation

struct EnvironmentStateDTO: Codable, Sendable {
    var id: UUID
    var timestamp: Date
    var temperature: Double?
    var humidity: Double?
}
