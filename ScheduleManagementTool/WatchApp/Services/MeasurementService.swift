import Foundation
import SwiftData
import Combine

@MainActor
final class MeasurementService: ObservableObject {
    private let healthKitService: HealthKitServicing
    private var modelContext: ModelContext
    private let debounceSeconds: TimeInterval
    private var timer: Timer?
    private var cancellables = Set<AnyCancellable>()

    @Published var isActive: Bool = false

    init(
        healthKitService: HealthKitServicing,
        modelContext: ModelContext,
        debounceSeconds: TimeInterval = 2.0
    ) {
        self.healthKitService = healthKitService
        self.modelContext = modelContext
        self.debounceSeconds = debounceSeconds
        observeHealthData()
    }

    func startMeasurement() async {
        guard await healthKitService.requestAuthorization() else { return }
        healthKitService.startMonitoring()
        startPeriodicSnapshot()
        isActive = true
    }

    func stopMeasurement() {
        healthKitService.stopMonitoring()
        timer?.invalidate()
        timer = nil
        isActive = false
    }

    private func observeHealthData() {
        healthKitService.heartRatePublisher
            .combineLatest(healthKitService.hrvPublisher)
            .debounce(for: .seconds(debounceSeconds), scheduler: RunLoop.main)
            .sink { [weak self] heartRate, hrv in
                self?.updateUserState(heartRate: heartRate, hrv: hrv)
            }
            .store(in: &cancellables)
    }

    private func updateUserState(heartRate: Double?, hrv: Double?) {
        let descriptor = FetchDescriptor<UserState>(
            sortBy: [SortDescriptor(\.timestamp, order: .reverse)]
        )
        guard let state = try? modelContext.fetch(descriptor).first else {
            let newState = UserState()
            newState.heartRateBpm = heartRate
            newState.hrvMs = hrv
            modelContext.insert(newState)
            try? modelContext.save()
            return
        }

        state.heartRateBpm = heartRate
        state.hrvMs = hrv
        state.timestamp = Date()
        try? modelContext.save()
    }

    private func startPeriodicSnapshot() {
        timer = Timer.scheduledTimer(withTimeInterval: 300, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.createPeriodicSnapshot()
            }
        }
    }

    private func createPeriodicSnapshot() {
        let descriptor = FetchDescriptor<UserState>(
            sortBy: [SortDescriptor(\.timestamp, order: .reverse)]
        )
        guard let state = try? modelContext.fetch(descriptor).first else { return }

        let record = UserStateHistoryRecord()
        record.heartRateBpm = state.heartRateBpm
        record.hrvMs = state.hrvMs
        record.valenceScore = state.valenceScore
        record.arousalScore = state.arousalScore
        record.focusScore = state.focusScore
        record.fatigueScore = state.fatigueScore
        record.isMeasurementActive = state.isMeasurementStateActive
        record.recordTypeRaw = "periodic"
        record.userState = state

        let sessionDescriptor = FetchDescriptor<MeasurementSession>(
            predicate: #Predicate { $0.statusRaw == "active" }
        )
        if let session = try? modelContext.fetch(sessionDescriptor).first {
            record.measurementSession = session
        }

        modelContext.insert(record)
        try? modelContext.save()
    }
}
