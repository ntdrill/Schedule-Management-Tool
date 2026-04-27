import SwiftUI
import SwiftData

struct FeedbackView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss
    @Query(sort: \UserState.timestamp, order: .reverse) private var userStates: [UserState]

    let executionRecord: ExecutionRecord

    @State private var userRating: Double = 3.0
    @State private var valence: Double = 3.0
    @State private var arousal: Double = 3.0
    @State private var focus: Double = 3.0
    @State private var fatigue: Double = 3.0

    private var currentUserState: UserState? { userStates.first }

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                Text(executionRecord.actionName)
                    .font(.headline)

                // User Rating
                VStack(alignment: .leading) {
                    Text("効果評価")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    HStack {
                        ForEach(1...5, id: \.self) { value in
                            Button {
                                userRating = Double(value)
                            } label: {
                                Image(systemName: value <= Int(userRating) ? "star.fill" : "star")
                                    .foregroundColor(.yellow)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }

                // Subjective Input
                VStack(spacing: 8) {
                    sliderRow(title: "快-不快", value: $valence)
                    sliderRow(title: "覚醒度", value: $arousal)
                    sliderRow(title: "集中度", value: $focus)
                    sliderRow(title: "疲労度", value: $fatigue)
                }

                Button {
                    saveEvaluation()
                } label: {
                    Text("保存")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .navigationTitle("評価")
    }

    private func sliderRow(title: String, value: Binding<Double>) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack {
                Text(title)
                    .font(.caption)
                Spacer()
                Text("\(Int(value.wrappedValue))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Slider(value: value, in: 1...5, step: 1)
        }
    }

    private func saveEvaluation() {
        // Update execution record rating
        executionRecord.userRating = userRating

        // Create EvaluationResult
        let matchScore = calculateMatchScore()
        let evaluation = EvaluationResult(matchScore: matchScore)
        modelContext.insert(evaluation)
        executionRecord.evaluationResult = evaluation

        // Create ActualStateSnapshot
        let snapshot = ActualStateSnapshot()
        if let state = currentUserState {
            snapshot.heartRateBpm = state.heartRateBpm
            snapshot.hrvMs = state.hrvMs
        }
        snapshot.valenceScore = valence
        snapshot.arousalScore = arousal
        snapshot.focusScore = focus
        snapshot.fatigueScore = fatigue
        snapshot.sourceDescription = "feedback_view"
        modelContext.insert(snapshot)

        // Update UserState with subjective input
        if let state = currentUserState {
            state.valenceScore = valence
            state.arousalScore = arousal
            state.focusScore = focus
            state.fatigueScore = fatigue
            state.timestamp = Date()
        }

        try? modelContext.save()
        dismiss()
    }

    private func calculateMatchScore() -> Double {
        // Simplified match score: normalized user rating
        return userRating / 5.0
    }
}
