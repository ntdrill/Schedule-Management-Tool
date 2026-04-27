import Foundation

struct SyncMessage: Codable, Sendable {
    var messageType: String
    var timestamp: Date
    var payload: Data

    init(messageType: String, payload: Data) {
        self.messageType = messageType
        self.timestamp = Date()
        self.payload = payload
    }
}
