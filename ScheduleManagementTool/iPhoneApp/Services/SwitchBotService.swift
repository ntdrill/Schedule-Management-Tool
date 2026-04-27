import Foundation

@MainActor
final class SwitchBotService: ObservableObject {
    @Published var latestTemperature: Double?
    @Published var latestHumidity: Double?
    @Published var lastError: String?

    private let baseURL = "https://api.switch-bot.com/v1.1"

    func fetchEnvironmentData(token: String, deviceId: String) async {
        guard !token.isEmpty, !deviceId.isEmpty else {
            lastError = "トークンまたはデバイスIDが未設定"
            return
        }

        let urlString = "\(baseURL)/devices/\(deviceId)/status"
        guard let url = URL(string: urlString) else {
            lastError = "無効なURL"
            return
        }

        var request = URLRequest(url: url)
        request.setValue(token, forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                lastError = "APIエラー"
                return
            }
            let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            if let body = json?["body"] as? [String: Any] {
                latestTemperature = body["temperature"] as? Double
                latestHumidity = body["humidity"] as? Double
                lastError = nil
            }
        } catch {
            lastError = error.localizedDescription
        }
    }
}
