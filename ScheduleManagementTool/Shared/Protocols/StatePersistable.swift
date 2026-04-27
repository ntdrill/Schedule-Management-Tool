import Foundation

protocol StatePersistable: Timestamped {
    func toSnapshot() -> [String: Any]
    func applyUpdate(from sensorData: SensorSnapshot)
}
