import Foundation
import SwiftData

@Model
final class EvaluationResult {
    var id: UUID = UUID()
    var timestamp: Date = Date()
    var matchScore: Double = 0.0
    var detailEvaluationJson: String?
    var expectedStateId: String?
    var notes: String?

    init(matchScore: Double) {
        self.matchScore = matchScore
    }
}
