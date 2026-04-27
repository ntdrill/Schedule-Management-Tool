import Foundation

struct SubjectiveInput: Codable, Equatable, Sendable {
    var valenceScore: Double
    var arousalScore: Double
    var focusScore: Double
    var fatigueScore: Double
    var inputTimestamp: Date

    init(valence: Double, arousal: Double, focus: Double,
         fatigue: Double, timestamp: Date = Date()) {
        self.valenceScore = valence
        self.arousalScore = arousal
        self.focusScore = focus
        self.fatigueScore = fatigue
        self.inputTimestamp = timestamp
    }
}
