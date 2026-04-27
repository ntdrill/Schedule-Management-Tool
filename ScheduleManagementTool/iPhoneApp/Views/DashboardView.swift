import SwiftUI
import SwiftData

struct DashboardView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \UserState.timestamp, order: .reverse) private var userStates: [UserState]
    @Query(sort: \EnvironmentState.timestamp, order: .reverse) private var environmentStates: [EnvironmentState]
    @Query(filter: #Predicate<MeasurementSession> { $0.statusRaw == "active" })
    private var activeSessions: [MeasurementSession]

    @StateObject private var switchBotService = SwitchBotService()
    @AppStorage("switchBotToken") private var switchBotToken: String = ""
    @AppStorage("switchBotDeviceId") private var switchBotDeviceId: String = ""

    private var currentUserState: UserState? { userStates.first }
    private var currentEnvironment: EnvironmentState? { environmentStates.first }
    private var activeSession: MeasurementSession? { activeSessions.first }
    private var isMeasuring: Bool { activeSession != nil }

    var body: some View {
        TabView {
            dashboardContent
                .tabItem {
                    Label("ダッシュボード", systemImage: "gauge.with.dots.needle.bottom.50percent")
                }

            HistoryLogView()
                .tabItem {
                    Label("ログ", systemImage: "clock.arrow.circlepath")
                }

            SettingsView()
                .tabItem {
                    Label("設定", systemImage: "gearshape")
                }
        }
    }

    private var dashboardContent: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    measurementToggleButton
                    measurementStatusCard
                    userStateCard
                    environmentCard
                }
                .padding()
            }
            .navigationTitle("ダッシュボード")
            .task(id: isMeasuring) {
                await runEnvironmentPollingLoop()
            }
        }
    }

    private func runEnvironmentPollingLoop() async {
        guard isMeasuring else { return }
        let intervalNs = UInt64(AppConstants.switchBotPollingIntervalSeconds * 1_000_000_000)
        while !Task.isCancelled {
            await pollAndPersistEnvironment()
            do {
                try await Task.sleep(nanoseconds: intervalNs)
            } catch {
                return
            }
        }
    }

    private func pollAndPersistEnvironment() async {
        guard !switchBotToken.isEmpty, !switchBotDeviceId.isEmpty else { return }
        await switchBotService.fetchEnvironmentData(token: switchBotToken, deviceId: switchBotDeviceId)
        let temperature = switchBotService.latestTemperature
        let humidity = switchBotService.latestHumidity
        guard temperature != nil || humidity != nil else { return }
        let snapshot = EnvironmentState()
        snapshot.temperature = temperature
        snapshot.humidity = humidity
        modelContext.insert(snapshot)
        try? modelContext.save()
    }

    private var measurementToggleButton: some View {
        Button {
            if isMeasuring {
                stopMeasurement()
            } else {
                startMeasurement()
            }
        } label: {
            HStack(spacing: 12) {
                Image(systemName: isMeasuring ? "stop.circle.fill" : "play.circle.fill")
                    .font(.system(size: 36))
                Text(isMeasuring ? "測定 OFF" : "測定 ON")
                    .font(.title2)
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 20)
        }
        .buttonStyle(.borderedProminent)
        .tint(isMeasuring ? .red : .blue)
        .controlSize(.large)
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

    private var measurementStatusCard: some View {
        HStack {
            Circle()
                .fill(isMeasuring ? .green : .gray)
                .frame(width: 12, height: 12)
            Text(isMeasuring ? "測定中" : "測定停止")
                .font(.headline)
            Spacer()
            if let session = activeSessions.first {
                Text(session.startTimestamp, style: .relative)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private var userStateCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("ユーザー状態")
                .font(.headline)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                stateItem(icon: "heart.fill", color: .red,
                         label: "心拍", value: currentUserState?.heartRateBpm.map { "\(Int($0)) bpm" } ?? "--")
                stateItem(icon: "waveform.path.ecg", color: .green,
                         label: "HRV", value: currentUserState?.hrvMs.map { "\(Int($0)) ms" } ?? "--")
                stateItem(icon: "face.smiling", color: .yellow,
                         label: "快-不快", value: currentUserState?.valenceScore.map { "\($0)/5" } ?? "--")
                stateItem(icon: "bolt.fill", color: .orange,
                         label: "覚醒度", value: currentUserState?.arousalScore.map { "\($0)/5" } ?? "--")
                stateItem(icon: "eye.fill", color: .purple,
                         label: "集中度", value: currentUserState?.focusScore.map { "\($0)/5" } ?? "--")
                stateItem(icon: "battery.50percent", color: .blue,
                         label: "疲労度", value: currentUserState?.fatigueScore.map { "\($0)/5" } ?? "--")
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private var environmentCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("環境データ")
                .font(.headline)
            HStack(spacing: 24) {
                stateItem(icon: "thermometer", color: .orange,
                         label: "室温", value: currentEnvironment?.temperature.map { String(format: "%.1f°C", $0) } ?? "--")
                stateItem(icon: "humidity.fill", color: .cyan,
                         label: "湿度", value: currentEnvironment?.humidity.map { String(format: "%.0f%%", $0) } ?? "--")
            }
            if let env = currentEnvironment {
                Text("更新: \(env.timestamp.formatted(date: .omitted, time: .shortened))")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private func stateItem(icon: String, color: Color, label: String, value: String) -> some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 20)
            VStack(alignment: .leading) {
                Text(label)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(value)
                    .font(.subheadline)
                    .fontWeight(.medium)
            }
        }
    }
}
