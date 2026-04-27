import Foundation

struct ExecutionRecordDTO: Codable, Sendable {
    var id: UUID
    var actionTemplateId: String
    var actionName: String
    var startTimestamp: Date
    var endTimestamp: Date?
    var userRating: Double?
    var measurementSessionId: UUID?
    var stateBeforeId: UUID?
    var stateAfterId: UUID?
    var evaluationResultId: UUID?
}
