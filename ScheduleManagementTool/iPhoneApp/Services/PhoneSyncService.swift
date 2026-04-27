import Foundation
import WatchConnectivity
import SwiftData

final class PhoneSyncService: NSObject, ObservableObject, WCSessionDelegate {
    static let shared = PhoneSyncService()

    @Published var isWatchReachable: Bool = false
    var modelContext: ModelContext?

    private override init() {
        super.init()
    }

    func activate() {
        guard WCSession.isSupported() else { return }
        let session = WCSession.default
        session.delegate = self
        session.activate()
    }

    // MARK: - Send to Watch (Application Context)

    func sendSettingsToWatch(presets: [ExpectedStateSchema], templates: [ActionTemplate], environment: EnvironmentState?) {
        var context: [String: Any] = [:]

        let presetDicts: [[String: Any]] = presets.map { preset in
            ["id": preset.id.uuidString,
             "name": preset.name,
             "presetType": preset.presetTypeRaw,
             "displayOrder": preset.displayOrder]
        }
        if let presetsData = try? JSONSerialization.data(withJSONObject: presetDicts) {
            context["presets"] = presetsData
        }

        if let templatesData = try? JSONEncoder().encode(templates) {
            context["templates"] = templatesData
        }

        if let env = environment,
           let envData = try? JSONEncoder().encode(EnvironmentStateDTO(
               id: env.id, timestamp: env.timestamp,
               temperature: env.temperature, humidity: env.humidity
           )) {
            context["environment"] = envData
        }

        try? WCSession.default.updateApplicationContext(context)
    }

    // MARK: - Receive from Watch

    func session(_ session: WCSession, didReceiveMessageData messageData: Data) {
        guard let syncMessage = try? JSONDecoder().decode(SyncMessage.self, from: messageData) else { return }
        Task { @MainActor in
            self.processSyncMessage(syncMessage)
        }
    }

    func session(_ session: WCSession, didReceiveUserInfo userInfo: [String: Any] = [:]) {
        guard let data = userInfo["syncMessage"] as? Data,
              let syncMessage = try? JSONDecoder().decode(SyncMessage.self, from: data) else { return }
        Task { @MainActor in
            self.processSyncMessage(syncMessage)
        }
    }

    @MainActor
    private func processSyncMessage(_ message: SyncMessage) {
        guard let context = modelContext else { return }
        let decoder = JSONDecoder()

        switch message.messageType {
        case "userState":
            guard let dto = try? decoder.decode(UserStateDTO.self, from: message.payload) else { return }
            upsertUserState(dto: dto, in: context)
        case "executionRecord":
            guard let dto = try? decoder.decode(ExecutionRecordDTO.self, from: message.payload) else { return }
            upsertExecutionRecord(dto: dto, in: context)
        case "measurementSession":
            guard let dto = try? decoder.decode(MeasurementSessionDTO.self, from: message.payload) else { return }
            upsertMeasurementSession(dto: dto, in: context)
        case "historyRecord":
            guard let dto = try? decoder.decode(UserStateHistoryRecordDTO.self, from: message.payload) else { return }
            insertHistoryRecord(dto: dto, in: context)
        case "evaluationResult":
            guard let dto = try? decoder.decode(EvaluationResultDTO.self, from: message.payload) else { return }
            insertEvaluationResult(dto: dto, in: context)
        default:
            break
        }
        try? context.save()
    }

    private func upsertUserState(dto: UserStateDTO, in context: ModelContext) {
        let descriptor = FetchDescriptor<UserState>(
            predicate: #Predicate { $0.id == dto.id }
        )
        if let existing = try? context.fetch(descriptor).first {
            existing.timestamp = dto.timestamp
            existing.heartRateBpm = dto.heartRateBpm
            existing.hrvMs = dto.hrvMs
            existing.valenceScore = dto.valenceScore
            existing.arousalScore = dto.arousalScore
            existing.focusScore = dto.focusScore
            existing.fatigueScore = dto.fatigueScore
            existing.isMeasurementStateActive = dto.isMeasurementStateActive
        } else {
            let state = UserState()
            state.id = dto.id
            state.timestamp = dto.timestamp
            state.heartRateBpm = dto.heartRateBpm
            state.hrvMs = dto.hrvMs
            state.valenceScore = dto.valenceScore
            state.arousalScore = dto.arousalScore
            state.focusScore = dto.focusScore
            state.fatigueScore = dto.fatigueScore
            state.isMeasurementStateActive = dto.isMeasurementStateActive
            context.insert(state)
        }
    }

    private func upsertExecutionRecord(dto: ExecutionRecordDTO, in context: ModelContext) {
        let descriptor = FetchDescriptor<ExecutionRecord>(
            predicate: #Predicate { $0.id == dto.id }
        )
        if let existing = try? context.fetch(descriptor).first {
            existing.endTimestamp = dto.endTimestamp
            existing.userRating = dto.userRating
        } else {
            let record = ExecutionRecord(actionTemplateId: dto.actionTemplateId, actionName: dto.actionName)
            record.id = dto.id
            record.startTimestamp = dto.startTimestamp
            record.endTimestamp = dto.endTimestamp
            record.userRating = dto.userRating
            context.insert(record)
        }
    }

    private func upsertMeasurementSession(dto: MeasurementSessionDTO, in context: ModelContext) {
        let descriptor = FetchDescriptor<MeasurementSession>(
            predicate: #Predicate { $0.id == dto.id }
        )
        if let existing = try? context.fetch(descriptor).first {
            existing.endTimestamp = dto.endTimestamp
            existing.statusRaw = dto.statusRaw
            existing.measurementTimeDailyMinutes = dto.measurementTimeDailyMinutes
        } else {
            let session = MeasurementSession()
            session.id = dto.id
            session.startTimestamp = dto.startTimestamp
            session.endTimestamp = dto.endTimestamp
            session.statusRaw = dto.statusRaw
            session.measurementTimeDailyMinutes = dto.measurementTimeDailyMinutes
            context.insert(session)
        }
    }

    private func insertHistoryRecord(dto: UserStateHistoryRecordDTO, in context: ModelContext) {
        let descriptor = FetchDescriptor<UserStateHistoryRecord>(
            predicate: #Predicate { $0.id == dto.id }
        )
        guard (try? context.fetch(descriptor).first) == nil else { return }
        let record = UserStateHistoryRecord()
        record.id = dto.id
        record.timestamp = dto.timestamp
        record.heartRateBpm = dto.heartRateBpm
        record.hrvMs = dto.hrvMs
        record.valenceScore = dto.valenceScore
        record.arousalScore = dto.arousalScore
        record.focusScore = dto.focusScore
        record.fatigueScore = dto.fatigueScore
        record.temperature = dto.temperature
        record.humidity = dto.humidity
        record.expectedStateId = dto.expectedStateId
        record.isMeasurementActive = dto.isMeasurementActive
        record.recordTypeRaw = dto.recordTypeRaw
        context.insert(record)
    }

    private func insertEvaluationResult(dto: EvaluationResultDTO, in context: ModelContext) {
        let descriptor = FetchDescriptor<EvaluationResult>(
            predicate: #Predicate { $0.id == dto.id }
        )
        guard (try? context.fetch(descriptor).first) == nil else { return }
        let result = EvaluationResult(matchScore: dto.matchScore)
        result.id = dto.id
        result.timestamp = dto.timestamp
        result.detailEvaluationJson = dto.detailEvaluationJson
        result.expectedStateId = dto.expectedStateId
        result.notes = dto.notes
        context.insert(result)
    }

    // MARK: - WCSessionDelegate

    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        Task { @MainActor in
            self.isWatchReachable = session.isReachable
        }
    }

    func sessionDidBecomeInactive(_ session: WCSession) {}

    func sessionDidDeactivate(_ session: WCSession) {
        session.activate()
    }
}
