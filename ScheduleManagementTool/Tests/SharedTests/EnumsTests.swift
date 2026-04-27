import XCTest
@testable import ScheduleManagementTool

final class EnumsTests: XCTestCase {

    func testExpectedStatePresetCasesAndRawValues() {
        XCTAssertEqual(ExpectedStatePreset.allCases.count, 5)
        XCTAssertEqual(ExpectedStatePreset.standard.rawValue, "standard")
        XCTAssertEqual(ExpectedStatePreset.ready.rawValue, "ready")
        XCTAssertEqual(ExpectedStatePreset.focus.rawValue, "focus")
        XCTAssertEqual(ExpectedStatePreset.rest.rawValue, "rest")
        XCTAssertEqual(ExpectedStatePreset.sleep.rawValue, "sleep")
    }

    func testExpectedStatePresetRoundTripFromRawValue() {
        for preset in ExpectedStatePreset.allCases {
            let recovered = ExpectedStatePreset(rawValue: preset.rawValue)
            XCTAssertEqual(recovered, preset)
        }
        XCTAssertNil(ExpectedStatePreset(rawValue: "unknown"))
    }

    func testMeasurementSessionStatusRawValues() {
        XCTAssertEqual(MeasurementSessionStatus.idle.rawValue, "idle")
        XCTAssertEqual(MeasurementSessionStatus.active.rawValue, "active")
        XCTAssertEqual(MeasurementSessionStatus.completed.rawValue, "completed")
        XCTAssertEqual(MeasurementSessionStatus.cancelled.rawValue, "cancelled")
    }

    func testMeasurementCapabilityStatusRawValues() {
        XCTAssertEqual(MeasurementCapabilityStatus.normal.rawValue, "normal")
        XCTAssertEqual(MeasurementCapabilityStatus.degraded.rawValue, "degraded")
        XCTAssertEqual(MeasurementCapabilityStatus.recoveryPending.rawValue, "recoveryPending")
        XCTAssertEqual(MeasurementCapabilityStatus.unavailable.rawValue, "unavailable")
    }

    func testMeasurementSessionQualityRawValues() {
        XCTAssertEqual(MeasurementSessionQuality.high.rawValue, "high")
        XCTAssertEqual(MeasurementSessionQuality.normal.rawValue, "normal")
        XCTAssertEqual(MeasurementSessionQuality.low.rawValue, "low")
    }
}
