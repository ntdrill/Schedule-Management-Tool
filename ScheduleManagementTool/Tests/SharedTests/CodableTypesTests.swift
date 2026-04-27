import XCTest
@testable import ScheduleManagementTool

final class CodableTypesTests: XCTestCase {

    private func encoder() -> JSONEncoder {
        let e = JSONEncoder()
        e.dateEncodingStrategy = .iso8601
        return e
    }

    private func decoder() -> JSONDecoder {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        return d
    }

    func testSensorSnapshotCodableRoundTrip() throws {
        let original = SensorSnapshot(
            heartRateBpm: 72.5,
            hrvMs: 48.0,
            temperature: 23.4,
            humidity: 51.2,
            capturedAt: Date(timeIntervalSince1970: 1_700_000_000)
        )
        let data = try encoder().encode(original)
        let recovered = try decoder().decode(SensorSnapshot.self, from: data)
        XCTAssertEqual(recovered, original)
    }

    func testSensorSnapshotDefaultInit() {
        let snap = SensorSnapshot()
        XCTAssertNil(snap.heartRateBpm)
        XCTAssertNil(snap.hrvMs)
        XCTAssertNil(snap.temperature)
        XCTAssertNil(snap.humidity)
    }

    func testSubjectiveInputCodableRoundTrip() throws {
        let original = SubjectiveInput(
            valence: 4.0,
            arousal: 3.0,
            focus: 5.0,
            fatigue: 2.0,
            at: Date(timeIntervalSince1970: 1_700_000_000)
        )
        let data = try encoder().encode(original)
        let recovered = try decoder().decode(SubjectiveInput.self, from: data)
        XCTAssertEqual(recovered, original)
    }

    func testDeltaResultEmptyInitHasAllNilFields() {
        let delta = DeltaResult()
        XCTAssertNil(delta.valenceChange)
        XCTAssertNil(delta.arousalChange)
        XCTAssertNil(delta.focusChange)
        XCTAssertNil(delta.fatigueChange)
        XCTAssertNil(delta.heartRateChange)
        XCTAssertNil(delta.hrvChange)
        XCTAssertNil(delta.overallChangeScore)
    }

    func testDeltaResultCodableRoundTrip() throws {
        var original = DeltaResult()
        original.valenceChange = 0.5
        original.heartRateChange = -3.0
        original.overallChangeScore = 0.42
        let data = try encoder().encode(original)
        let recovered = try decoder().decode(DeltaResult.self, from: data)
        XCTAssertEqual(recovered, original)
    }
}
