import XCTest
import SwiftData
@testable import ScheduleManagementTool

@MainActor
final class MeasurementServiceTests: XCTestCase {

    private var container: ModelContainer!
    private var context: ModelContext!
    private var mock: MockHealthKitService!

    override func setUp() async throws {
        try await super.setUp()
        let schema = Schema([
            UserState.self,
            MeasurementSession.self,
            ExecutionRecord.self,
            UserStateHistoryRecord.self,
            EvaluationResult.self,
            ExpectedStateSchema.self,
            ActualStateSnapshot.self,
            EnvironmentState.self,
            DeviceConnectionStatusMap.self,
        ])
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        container = try ModelContainer(for: schema, configurations: [config])
        context = ModelContext(container)
        mock = MockHealthKitService()
    }

    override func tearDown() async throws {
        container = nil
        context = nil
        mock = nil
        try await super.tearDown()
    }

    func testIsActiveStartsFalse() {
        let service = MeasurementService(healthKitService: mock, modelContext: context)
        XCTAssertFalse(service.isActive)
    }

    func testStartMeasurementActivatesAndStartsMonitoring() async {
        let service = MeasurementService(healthKitService: mock, modelContext: context)
        await service.startMeasurement()
        XCTAssertTrue(service.isActive)
        XCTAssertEqual(mock.requestAuthorizationCallCount, 1)
        XCTAssertEqual(mock.startMonitoringCallCount, 1)
    }

    func testStartMeasurementSkipsWhenAuthorizationDenied() async {
        mock.authorizationResult = false
        let service = MeasurementService(healthKitService: mock, modelContext: context)
        await service.startMeasurement()
        XCTAssertFalse(service.isActive)
        XCTAssertEqual(mock.startMonitoringCallCount, 0)
    }

    func testStopMeasurementDeactivatesAndStopsMonitoring() async {
        let service = MeasurementService(healthKitService: mock, modelContext: context)
        await service.startMeasurement()
        service.stopMeasurement()
        XCTAssertFalse(service.isActive)
        XCTAssertEqual(mock.stopMonitoringCallCount, 1)
    }

    func testHealthKitPublisherUpdatesPersistsToUserState() async throws {
        let service = MeasurementService(
            healthKitService: mock,
            modelContext: context,
            debounceSeconds: 0.05
        )
        _ = service

        mock.latestHeartRate = 72
        mock.latestHRV = 45

        let deadline = Date().addingTimeInterval(2.0)
        var fetched: UserState?
        while Date() < deadline {
            try await Task.sleep(nanoseconds: 100_000_000)
            let descriptor = FetchDescriptor<UserState>(
                sortBy: [SortDescriptor(\.timestamp, order: .reverse)]
            )
            if let state = try context.fetch(descriptor).first,
               state.heartRateBpm == 72,
               state.hrvMs == 45 {
                fetched = state
                break
            }
        }
        XCTAssertNotNil(fetched, "updateUserState should persist the latest heart rate and HRV from the publisher")
    }
}
