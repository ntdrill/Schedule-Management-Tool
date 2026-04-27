import SwiftUI
import SwiftData

struct MainView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \UserState.timestamp, order: .reverse) private var userStates: [UserState]
    @Query(sort: \EnvironmentState.timestamp, order: .reverse) private var environmentStates: [EnvironmentState]
    @Query(filter: #Predicate<MeasurementSession> { $0.statusRaw == "active" })
    private var activeSessions: [MeasurementSession]
    @Query(sort: \ExpectedStateSchema.displayOrder) private var presets: [ExpectedStateSchema]

    @State private var selectedPresetId: String?

    private var currentUserState: UserState? { userStates.first }
    private var currentEnvironment: EnvironmentState? { environmentStates.first }
    private var activeSession: MeasurementSession? { activeSessions.first }
    private var isMeasuring: Bool { activeSession != nil }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 12) {
                    // Sensor Data
                    sensorSection

                    // Measurement Toggle
                    measurementToggle

                    // Expected State
                    expectedStateSection
                }
                .padding()
            }
            .navigationTitle("状態")
            .onAppear {
                if selectedPresetId == nil {
                    selectedPresetId = currentUserState?.expectedStateId
                }
            }
            .onChange(of: selectedPresetId) { _, newValue in
                persistExpectedState(newValue)
            }
        }
    }

    private var sensorSection: some View {
        VStack(spacing: 8) {
            HStack {
                Label {
                    Text(currentUserState?.heartRateBpm.map { "\(Int($0))" } ?? "--")
                } icon: {
                    Image(systemName: "heart.fill")
                        .foregroundColor(.red)
                }
                Spacer()
                Label {
                    Text(currentUserState?.hrvMs.map { "\(Int($0))ms" } ?? "--")
                } icon: {
                    Image(systemName: "waveform.path.ecg")
                        .foregroundColor(.green)
                }
            }
            .font(.title3)

            HStack {
                Label {
                    Text(currentEnvironment?.temperature.map { String(format: "%.1f°", $0) } ?? "--°")
                } icon: {
                    Image(systemName: "thermometer")
                        .foregroundColor(.orange)
                }
                Spacer()
                Label {
                    Text(currentEnvironment?.humidity.map { String(format: "%.0f%%", $0) } ?? "--%")
                } icon: {
                    Image(systemName: "humidity.fill")
                        .foregroundColor(.cyan)
                }
            }
            .font(.caption)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private var measurementToggle: some View {
        Button {
            if isMeasuring {
                stopMeasurement()
            } else {
                startMeasurement()
            }
        } label: {
            HStack {
                Image(systemName: isMeasuring ? "stop.circle.fill" : "play.circle.fill")
                    .font(.title2)
                Text(isMeasuring ? "測定 OFF" : "測定 ON")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
        }
        .buttonStyle(.borderedProminent)
        .tint(isMeasuring ? .red : .blue)
    }

    private var expectedStateSection: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("期待状態")
                .font(.caption)
                .foregroundColor(.secondary)
            if let preset = presets.first(where: { $0.presetTypeRaw == selectedPresetId }) {
                Text(preset.name)
                    .font(.headline)
            } else {
                Text("未選択")
                    .font(.headline)
                    .foregroundColor(.secondary)
            }

            Picker("プリセット", selection: $selectedPresetId) {
                Text("未選択").tag(nil as String?)
                ForEach(presets, id: \.id) { preset in
                    Text(preset.name).tag(preset.presetTypeRaw as String?)
                }
            }
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private func startMeasurement() {
        let session = MeasurementSession()
        session.statusRaw = MeasurementSessionStatus.active.rawValue
        session.isMeasurementMode = true
        modelContext.insert(session)

        if let state = currentUserState {
            state.isMeasurementStateActive = true
            state.timestamp = Date()
        } else {
            let newState = UserState()
            newState.isMeasurementStateActive = true
            modelContext.insert(newState)
        }
        try? modelContext.save()
    }

    private func persistExpectedState(_ newValue: String?) {
        if let state = currentUserState {
            guard state.expectedStateId != newValue else { return }
            state.expectedStateId = newValue
            state.timestamp = Date()
        } else {
            let newState = UserState()
            newState.expectedStateId = newValue
            modelContext.insert(newState)
        }
        try? modelContext.save()
    }

    private func stopMeasurement() {
        guard let session = activeSession else { return }
        session.endTimestamp = Date()
        session.statusRaw = MeasurementSessionStatus.completed.rawValue
        session.isMeasurementMode = false

        if let elapsed = Calendar.current.dateComponents([.minute], from: session.startTimestamp, to: Date()).minute {
            session.measurementTimeDailyMinutes += Double(elapsed)
        }

        if let state = currentUserState {
            state.isMeasurementStateActive = false
            state.timestamp = Date()
        }
        try? modelContext.save()
    }
}
