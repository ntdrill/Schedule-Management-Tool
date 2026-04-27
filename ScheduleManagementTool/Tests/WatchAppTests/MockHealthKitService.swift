import Foundation
import Combine
@testable import ScheduleManagementTool

@MainActor
final class MockHealthKitService: HealthKitServicing {
    @Published var latestHeartRate: Double?
    @Published var latestHRV: Double?

    var heartRatePublisher: AnyPublisher<Double?, Never> { $latestHeartRate.eraseToAnyPublisher() }
    var hrvPublisher: AnyPublisher<Double?, Never> { $latestHRV.eraseToAnyPublisher() }

    var authorizationResult: Bool = true
    private(set) var requestAuthorizationCallCount: Int = 0
    private(set) var startMonitoringCallCount: Int = 0
    private(set) var stopMonitoringCallCount: Int = 0

    func requestAuthorization() async -> Bool {
        requestAuthorizationCallCount += 1
        return authorizationResult
    }

    func startMonitoring() {
        startMonitoringCallCount += 1
    }

    func stopMonitoring() {
        stopMonitoringCallCount += 1
    }
}
