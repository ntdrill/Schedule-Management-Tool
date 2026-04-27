import XCTest
@testable import ScheduleManagementTool

final class ModelDefaultsTests: XCTestCase {

    func testUserStateDefaults() {
        let user = UserState()
        XCTAssertFalse(user.isMeasurementStateActive)
        XCTAssertEqual(user.measurementCapabilityStatusRaw, "normal")
        XCTAssertNil(user.heartRateBpm)
        XCTAssertNil(user.hrvMs)
        XCTAssertNil(user.expectedStateId)
        XCTAssertTrue(user.historyRecords.isEmpty)
    }

    func testMeasurementSessionDefaults() {
        let session = MeasurementSession()
        XCTAssertEqual(session.statusRaw, "active")
        XCTAssertEqual(session.measurementTimeDailyMinutes, 0.0)
        XCTAssertTrue(session.isMeasurementMode)
        XCTAssertNil(session.endTimestamp)
        XCTAssertTrue(session.executionRecords.isEmpty)
        XCTAssertTrue(session.stateRecords.isEmpty)
    }

    func testMeasurementSessionStatusRawMatchesEnumActive() {
        let session = MeasurementSession()
        XCTAssertEqual(session.statusRaw, MeasurementSessionStatus.active.rawValue)
    }

    func testUserStateCapabilityStatusRawMatchesEnumNormal() {
        let user = UserState()
        XCTAssertEqual(user.measurementCapabilityStatusRaw, MeasurementCapabilityStatus.normal.rawValue)
    }

    func testExecutionRecordInitPersistsTemplateInfo() {
        let record = ExecutionRecord(actionTemplateId: "tpl-001", actionName: "深呼吸")
        XCTAssertEqual(record.actionTemplateId, "tpl-001")
        XCTAssertEqual(record.actionName, "深呼吸")
        XCTAssertNil(record.endTimestamp)
        XCTAssertNil(record.userRating)
    }

    func testExpectedStateSchemaInitPersistsName() {
        let schema = ExpectedStateSchema(name: "Focus", presetType: ExpectedStatePreset.focus.rawValue)
        XCTAssertEqual(schema.name, "Focus")
        XCTAssertEqual(schema.presetTypeRaw, "focus")
        XCTAssertEqual(schema.displayOrder, 0)
        XCTAssertTrue(schema.isSystemPreset)
    }

    func testEvaluationResultInitPersistsScore() {
        let result = EvaluationResult(matchScore: 0.85)
        XCTAssertEqual(result.matchScore, 0.85)
        XCTAssertNil(result.expectedStateId)
        XCTAssertNil(result.notes)
    }
}
