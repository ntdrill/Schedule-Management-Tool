import SwiftUI
import SwiftData

struct SettingsView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \ExpectedStateSchema.displayOrder) private var presets: [ExpectedStateSchema]

    @AppStorage("switchBotToken") private var switchBotToken: String = ""
    @AppStorage("switchBotDeviceId") private var switchBotDeviceId: String = ""

    @State private var actionTemplates: [ActionTemplate] = AppConstants.defaultActionTemplates

    var body: some View {
        NavigationStack {
            Form {
                Section("SwitchBot 連携") {
                    SecureField("API トークン", text: $switchBotToken)
                    TextField("デバイス ID", text: $switchBotDeviceId)
                }

                Section("期待状態プリセット") {
                    ForEach(presets, id: \.id) { preset in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(preset.name).font(.body)
                                Text(preset.presetTypeRaw).font(.caption).foregroundColor(.secondary)
                            }
                            Spacer()
                            if preset.isSystemPreset {
                                Text("システム").font(.caption2).foregroundColor(.secondary)
                            }
                        }
                    }
                    Button("プリセットを初期化") { seedDefaultPresets() }
                }

                Section("対処行動テンプレート") {
                    ForEach(actionTemplates) { template in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(template.name)
                                if let category = template.category {
                                    Text(category).font(.caption).foregroundColor(.secondary)
                                }
                            }
                            Spacer()
                            if let sec = template.estimatedDurationSeconds {
                                Text("\(sec / 60)分").font(.caption).foregroundColor(.secondary)
                            }
                        }
                    }
                }

                Section("アプリ情報") {
                    HStack {
                        Text("バージョン"); Spacer()
                        Text("v1.0.0 (MVP)").foregroundColor(.secondary)
                    }
                    HStack {
                        Text("測定時間上限"); Spacer()
                        Text("\(Int(AppConstants.measurementLimitDailyMaxMinutes))分/日").foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("設定")
        }
    }

    private func seedDefaultPresets() {
        for preset in presets where preset.isSystemPreset {
            modelContext.delete(preset)
        }
        let defaults: [(String, String, Int, String?, String?, String?, String?, String)] = [
            ("標準", "standard", 0, "2-4", "2-4", "2-4", "2-4", "通常の覚醒状態"),
            ("準備完了", "ready", 1, "3-5", "3-4", "3-4", "1-3", "作業開始可能状態"),
            ("集中", "focus", 2, "3-5", "3-4", "4-5", "1-2", "深い集中状態"),
            ("休息", "rest", 3, "3-5", "1-2", "1-3", "2-4", "意識的な休息状態"),
            ("睡眠", "sleep", 4, "3-5", "1-2", "1-2", "3-5", "入眠準備/睡眠中"),
        ]
        for (name, type, order, valence, arousal, focus, fatigue, desc) in defaults {
            let schema = ExpectedStateSchema(name: name, presetType: type)
            schema.displayOrder = order
            schema.targetValenceRange = valence
            schema.targetArousalRange = arousal
            schema.targetFocusRange = focus
            schema.targetFatigueRange = fatigue
            schema.descriptionText = desc
            modelContext.insert(schema)
        }
        try? modelContext.save()
    }
}
