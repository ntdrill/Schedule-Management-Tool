import SwiftUI
import SwiftData

struct HistoryLogView: View {
    @Query(sort: \UserStateHistoryRecord.timestamp, order: .reverse)
    private var historyRecords: [UserStateHistoryRecord]
    @Query(sort: \ExecutionRecord.startTimestamp, order: .reverse)
    private var executionRecords: [ExecutionRecord]
    @Query(sort: \MeasurementSession.startTimestamp, order: .reverse)
    private var sessions: [MeasurementSession]

    @State private var selectedTab = 0

    var body: some View {
        NavigationStack {
            VStack {
                Picker("表示", selection: $selectedTab) {
                    Text("状態").tag(0)
                    Text("行動").tag(1)
                    Text("セッション").tag(2)
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)

                switch selectedTab {
                case 0: stateHistoryList
                case 1: executionList
                default: sessionList
                }
            }
            .navigationTitle("ログ")
        }
    }

    private var stateHistoryList: some View {
        List(historyRecords, id: \.id) { record in
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(record.timestamp.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(record.recordTypeRaw)
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(recordTypeBadgeColor(record.recordTypeRaw).opacity(0.2))
                        .cornerRadius(4)
                }
                HStack(spacing: 12) {
                    if let hr = record.heartRateBpm {
                        Label("\(Int(hr))bpm", systemImage: "heart.fill").font(.caption)
                    }
                    if let hrv = record.hrvMs {
                        Label("\(Int(hrv))ms", systemImage: "waveform.path.ecg").font(.caption)
                    }
                }
                if record.valenceScore != nil || record.arousalScore != nil {
                    HStack(spacing: 8) {
                        if let v = record.valenceScore { Text("快:\(Int(v))").font(.caption2) }
                        if let a = record.arousalScore { Text("覚:\(Int(a))").font(.caption2) }
                        if let f = record.focusScore { Text("集:\(Int(f))").font(.caption2) }
                        if let ft = record.fatigueScore { Text("疲:\(Int(ft))").font(.caption2) }
                    }
                    .foregroundColor(.secondary)
                }
            }
            .padding(.vertical, 2)
        }
    }

    private var executionList: some View {
        List(executionRecords, id: \.id) { record in
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(record.actionName).font(.headline)
                    Spacer()
                    if let rating = record.userRating {
                        HStack(spacing: 2) {
                            ForEach(1...5, id: \.self) { i in
                                Image(systemName: i <= Int(rating) ? "star.fill" : "star")
                                    .font(.caption2).foregroundColor(.yellow)
                            }
                        }
                    }
                }
                Text(record.startTimestamp.formatted(date: .abbreviated, time: .shortened))
                    .font(.caption).foregroundColor(.secondary)
                if let end = record.endTimestamp {
                    let duration = end.timeIntervalSince(record.startTimestamp)
                    Text("所要時間: \(Int(duration / 60))分").font(.caption).foregroundColor(.secondary)
                }
                if let eval = record.evaluationResult {
                    Text("一致スコア: \(String(format: "%.0f%%", eval.matchScore * 100))")
                        .font(.caption).foregroundColor(.blue)
                }
            }
            .padding(.vertical, 2)
        }
    }

    private var sessionList: some View {
        List(sessions, id: \.id) { session in
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Circle()
                        .fill(session.statusRaw == "active" ? .green : .gray)
                        .frame(width: 8, height: 8)
                    Text(session.statusRaw).font(.caption).textCase(.uppercase)
                    Spacer()
                }
                Text("開始: \(session.startTimestamp.formatted(date: .abbreviated, time: .shortened))").font(.caption)
                if let end = session.endTimestamp {
                    Text("終了: \(end.formatted(date: .abbreviated, time: .shortened))").font(.caption)
                }
                Text("累積: \(Int(session.measurementTimeDailyMinutes))分").font(.caption).foregroundColor(.secondary)
            }
            .padding(.vertical, 2)
        }
    }

    private func recordTypeBadgeColor(_ type: String) -> Color {
        switch type {
        case "actionBefore": return .orange
        case "actionAfter": return .green
        default: return .blue
        }
    }
}
