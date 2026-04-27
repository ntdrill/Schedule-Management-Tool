import Foundation
import Combine

@MainActor
protocol HealthKitServicing: AnyObject {
    var latestHeartRate: Double? { get }
    var latestHRV: Double? { get }

    var heartRatePublisher: AnyPublisher<Double?, Never> { get }
    var hrvPublisher: AnyPublisher<Double?, Never> { get }

    func requestAuthorization() async -> Bool
    func startMonitoring()
    func stopMonitoring()
}
