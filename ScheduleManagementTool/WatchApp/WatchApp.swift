import SwiftUI
import SwiftData

@main
struct ScheduleManagementWatchApp: App {
    var sharedModelContainer: ModelContainer = {
        let schema = Schema([
            UserState.self,
            MeasurementSession.self,
            ExecutionRecord.self,
            UserStateHistoryRecord.self,
            EvaluationResult.self,
            ExpectedStateSchema.self,
            ActualStateSnapshot.self,
            EnvironmentState.self,
            DeviceConnectionStatusMap.self,
        ])
        let modelConfiguration = ModelConfiguration(
            "WatchStore",
            schema: schema,
            isStoredInMemoryOnly: false
        )
        do {
            return try ModelContainer(for: schema, configurations: [modelConfiguration])
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()

    var body: some Scene {
        WindowGroup {
            MainView()
        }
        .modelContainer(sharedModelContainer)
    }
}
