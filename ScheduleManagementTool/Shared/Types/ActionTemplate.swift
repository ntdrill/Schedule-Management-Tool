import Foundation

struct ActionTemplate: Codable, Identifiable, Sendable {
    var id: String
    var name: String
    var category: String?
    var estimatedDurationSeconds: Int?
    var isSystemPreset: Bool = true
    var displayOrder: Int = 0
}
