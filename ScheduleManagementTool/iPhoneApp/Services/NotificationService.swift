import Foundation
import UserNotifications

final class NotificationService {
    static let shared = NotificationService()

    private init() {}

    func requestAuthorization() async -> Bool {
        do {
            return try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .sound, .badge])
        } catch {
            print("Notification authorization failed: \(error)")
            return false
        }
    }

    func scheduleMeasurementReminder(afterMinutes minutes: Int = 60) {
        let content = UNMutableNotificationContent()
        content.title = "測定リマインダー"
        content.body = "長時間の測定が続いています。休憩を検討してください。"
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: TimeInterval(minutes * 60), repeats: false
        )
        let request = UNNotificationRequest(
            identifier: "measurement_reminder_\(UUID().uuidString)",
            content: content, trigger: trigger
        )
        UNUserNotificationCenter.current().add(request)
    }

    func scheduleActionTimeReminder(actionName: String, afterMinutes minutes: Int = 30) {
        let content = UNMutableNotificationContent()
        content.title = "行動経過通知"
        content.body = "「\(actionName)」を開始してから\(minutes)分が経過しました。"
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: TimeInterval(minutes * 60), repeats: false
        )
        let request = UNNotificationRequest(
            identifier: "action_reminder_\(UUID().uuidString)",
            content: content, trigger: trigger
        )
        UNUserNotificationCenter.current().add(request)
    }

    func cancelAllPendingNotifications() {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }
}
