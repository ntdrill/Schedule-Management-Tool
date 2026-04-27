import Foundation
import SwiftData

@Model
final class ExpectedStateSchema {
    var id: UUID = UUID()
    var name: String = ""
    var presetTypeRaw: String = "standard"
    var displayOrder: Int = 0
    var isSystemPreset: Bool = true

    var targetValenceRange: String?
    var targetArousalRange: String?
    var targetFocusRange: String?
    var targetFatigueRange: String?
    var descriptionText: String?

    var stateVectorJson: String?

    init(name: String, presetType: String) {
        self.name = name
        self.presetTypeRaw = presetType
    }
}
