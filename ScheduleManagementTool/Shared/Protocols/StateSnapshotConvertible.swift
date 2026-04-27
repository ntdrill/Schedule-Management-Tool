import Foundation

protocol StateSnapshotConvertible {
    func createHistoryRecord() -> UserStateHistoryRecord
    func createActualSnapshot() -> ActualStateSnapshot
}
