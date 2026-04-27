import Foundation
import SwiftData

@Model
final class ExecutionRecord {
    var id: UUID = UUID()
    var actionTemplateId: String = ""
    var actionName: String = ""
    var startTimestamp: Date = Date()
    var endTimestamp: Date?

    // --- 主観評価 [1-5] ---
    var userRating: Double?

    // --- Relationship ---
    var measurementSession: MeasurementSession?

    @Relationship(deleteRule: .nullify)
    var stateBefore: UserStateHistoryRecord?

    @Relationship(deleteRule: .nullify)
    var stateAfter: UserStateHistoryRecord?

    @Relationship(deleteRule: .cascade)
    var evaluationResult: EvaluationResult?

    init(actionTemplateId: String, actionName: String) {
        self.actionTemplateId = actionTemplateId
        self.actionName = actionName
    }
}
