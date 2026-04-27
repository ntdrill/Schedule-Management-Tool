import Foundation
import Combine
import HealthKit

@MainActor
final class HealthKitService: ObservableObject, HealthKitServicing {
    private let healthStore = HKHealthStore()
    private var heartRateQuery: HKAnchoredObjectQuery?
    private var hrvQuery: HKAnchoredObjectQuery?

    @Published var latestHeartRate: Double?
    @Published var latestHRV: Double?
    @Published var isAuthorized: Bool = false

    var heartRatePublisher: AnyPublisher<Double?, Never> { $latestHeartRate.eraseToAnyPublisher() }
    var hrvPublisher: AnyPublisher<Double?, Never> { $latestHRV.eraseToAnyPublisher() }

    private let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
    private let hrvType = HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!

    func requestAuthorization() async -> Bool {
        guard HKHealthStore.isHealthDataAvailable() else { return false }

        let typesToRead: Set<HKSampleType> = [heartRateType, hrvType]

        do {
            try await healthStore.requestAuthorization(toShare: [], read: typesToRead)
            isAuthorized = true
            return true
        } catch {
            print("HealthKit authorization failed: \(error)")
            return false
        }
    }

    func startMonitoring() {
        startHeartRateMonitoring()
        startHRVMonitoring()
    }

    func stopMonitoring() {
        if let query = heartRateQuery {
            healthStore.stop(query)
            heartRateQuery = nil
        }
        if let query = hrvQuery {
            healthStore.stop(query)
            hrvQuery = nil
        }
    }

    private func startHeartRateMonitoring() {
        let predicate = HKQuery.predicateForSamples(
            withStart: Date(),
            end: nil,
            options: .strictStartDate
        )

        let query = HKAnchoredObjectQuery(
            type: heartRateType,
            predicate: predicate,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { [weak self] _, samples, _, _, _ in
            self?.processHeartRateSamples(samples)
        }

        query.updateHandler = { [weak self] _, samples, _, _, _ in
            self?.processHeartRateSamples(samples)
        }

        healthStore.execute(query)
        heartRateQuery = query
    }

    private func startHRVMonitoring() {
        let predicate = HKQuery.predicateForSamples(
            withStart: Date(),
            end: nil,
            options: .strictStartDate
        )

        let query = HKAnchoredObjectQuery(
            type: hrvType,
            predicate: predicate,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { [weak self] _, samples, _, _, _ in
            self?.processHRVSamples(samples)
        }

        query.updateHandler = { [weak self] _, samples, _, _, _ in
            self?.processHRVSamples(samples)
        }

        healthStore.execute(query)
        hrvQuery = query
    }

    private func processHeartRateSamples(_ samples: [HKSample]?) {
        guard let quantitySamples = samples as? [HKQuantitySample],
              let latest = quantitySamples.last else { return }

        let bpm = latest.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
        Task { @MainActor in
            self.latestHeartRate = bpm
        }
    }

    private func processHRVSamples(_ samples: [HKSample]?) {
        guard let quantitySamples = samples as? [HKQuantitySample],
              let latest = quantitySamples.last else { return }

        let ms = latest.quantity.doubleValue(for: .secondUnit(with: .milli))
        Task { @MainActor in
            self.latestHRV = ms
        }
    }
}
