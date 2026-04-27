import SwiftUI
import SwiftData

struct ActionView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \UserState.timestamp, order: .reverse) private var userStates: [UserState]
    @Query(filter: #Predicate<MeasurementSession> { $0.statusRaw == "active" })
    private var activeSessions: [MeasurementSession]

    @State private var templates: [ActionTemplate] = AppConstants.defaultActionTemplates
    @State private var activeRecord: ExecutionRecord?
    @State private var showFeedback = false
    @State private var completedRecord: ExecutionRecord?

    private var currentUserState: UserState? { userStates.first }

    var body: some View {
        NavigationStack {
            List {
                if let record = activeRecord {
                    activeActionSection(record: record)
                } else {
                    templateListSection
                }
            }
            .navigationTitle("対処行動")
            .navigationDestination(isPresented: $showFeedback) {
                if let record = completedRecord {
                    FeedbackView(executionRecord: record)
                }
            }
        }
    }

    private func activeActionSection(record: ExecutionRecord) -> some View {
        Section("実行中") {
            VStack(alignment: .leading, spacing: 8) {
                Text(record.actionName)
                    .font(.headline)
                Text("開始: \(record.startTimestamp.formatted(date: .omitted, time: .shortened))")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Button {
                    stopAction(record: record)
                } label: {
                    HStack {
                        Image(systemName: "stop.circle.fill")
                        Text("終了")
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.orange)
            }
        }
    }

    private var templateListSection: some View {
        Section("行動を選択") {
            ForEach(templates) { template in
                Button {
                    startAction(template: template)
                } label: {
                    HStack {
                        VStack(alignment: .leading) {
                            Text(template.name)
                                .font(.headline)
                            if let category = template.category {
                                Text(category)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        Spacer()
                        if let duration = template.estimatedDurationSeconds {
                            Text("\(duration / 60)分")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
        }
    }

    private func startAction(template: ActionTemplate) {
        let record = ExecutionRecord(actionTemplateId: template.id, actionName: template.name)
        modelContext.insert(record)

        // Create stateBefore snapshot
        let before = createHistoryRecord(type: "actionBefore")
        modelContext.insert(before)
        record.stateBefore = before

        if let session = activeSessions.first {
            record.measurementSession = session
        }

        try? modelContext.save()
        activeRecord = record
    }

    private func stopAction(record: ExecutionRecord) {
        record.endTimestamp = Date()

        // Create stateAfter snapshot
        let after = createHistoryRecord(type: "actionAfter")
        modelContext.insert(after)
        record.stateAfter = after

        try? modelContext.save()
        completedRecord = record
        activeRecord = nil
        showFeedback = true
    }

    private func createHistoryRecord(type: String) -> UserStateHistoryRecord {
        let record = UserStateHistoryRecord()
        if let state = currentUserState {
            record.heartRateBpm = state.heartRateBpm
            record.hrvMs = state.hrvMs
            record.valenceScore = state.valenceScore
            record.arousalScore = state.arousalScore
            record.focusScore = state.focusScore
            record.fatigueScore = state.fatigueScore
            record.isMeasurementActive = state.isMeasurementStateActive
            record.userState = state
        }
        if let session = activeSessions.first {
            record.measurementSession = session
        }
        record.recordTypeRaw = type
        return record
    }
}
