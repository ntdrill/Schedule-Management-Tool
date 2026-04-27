import Foundation
import WatchConnectivity

final class WatchSyncService: NSObject, ObservableObject, WCSessionDelegate {
    static let shared = WatchSyncService()

    @Published var isReachable: Bool = false

    private override init() {
        super.init()
    }

    func activate() {
        guard WCSession.isSupported() else { return }
        let session = WCSession.default
        session.delegate = self
        session.activate()
    }

    // MARK: - Send Methods

    func sendUserStateUpdate(_ dto: UserStateDTO) {
        guard let data = try? JSONEncoder().encode(dto) else { return }
        let message = SyncMessage(messageType: "userState", payload: data)
        sendRealtime(message)
    }

    func sendMeasurementStatusChange(_ dto: MeasurementSessionDTO) {
        guard let data = try? JSONEncoder().encode(dto) else { return }
        let message = SyncMessage(messageType: "measurementSession", payload: data)
        sendRealtime(message)
    }

    func transferRecord(_ syncMessage: SyncMessage) {
        guard let data = try? JSONEncoder().encode(syncMessage) else { return }
        WCSession.default.transferUserInfo(["syncMessage": data])
    }

    private func sendRealtime(_ message: SyncMessage) {
        guard WCSession.default.isReachable,
              let data = try? JSONEncoder().encode(message) else { return }
        WCSession.default.sendMessageData(data, replyHandler: nil, errorHandler: nil)
    }

    // MARK: - Receive (Application Context from iPhone)

    func session(_ session: WCSession, didReceiveApplicationContext applicationContext: [String: Any]) {
        NotificationCenter.default.post(
            name: .didReceiveApplicationContext,
            object: nil,
            userInfo: applicationContext
        )
    }

    // MARK: - WCSessionDelegate

    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        Task { @MainActor in
            self.isReachable = session.isReachable
        }
    }
}

extension Notification.Name {
    static let didReceiveApplicationContext = Notification.Name("didReceiveApplicationContext")
}
