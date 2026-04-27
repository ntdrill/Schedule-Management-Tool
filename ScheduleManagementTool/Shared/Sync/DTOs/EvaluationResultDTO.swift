import Foundation

struct EvaluationResultDTO: Codable, Sendable {
    var id: UUID
    var timestamp: Date
    var matchScore: Double
    var detailEvaluationJson: String?
    var expectedStateId: String?
    var notes: String?
}
