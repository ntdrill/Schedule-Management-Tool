import XCTest

final class DashboardSmokeUITests: XCTestCase {

    override func setUpWithError() throws {
        try super.setUpWithError()
        continueAfterFailure = false
    }

    func test_appLaunch_showsThreeTabsAndCanNavigateToLog() throws {
        let app = XCUIApplication()
        app.launch()

        let tabBar = app.tabBars.firstMatch
        XCTAssertTrue(tabBar.waitForExistence(timeout: 10), "TabBar が表示されない")

        let dashboardTab = tabBar.buttons["ダッシュボード"]
        let logTab = tabBar.buttons["ログ"]
        let settingsTab = tabBar.buttons["設定"]

        XCTAssertTrue(dashboardTab.waitForExistence(timeout: 5), "ダッシュボードタブが見つからない")
        XCTAssertTrue(logTab.exists, "ログタブが見つからない")
        XCTAssertTrue(settingsTab.exists, "設定タブが見つからない")

        XCTAssertTrue(dashboardTab.isSelected, "起動直後はダッシュボードタブが選択されているはず")

        logTab.tap()
        XCTAssertTrue(logTab.isSelected, "ログタブをタップしても選択状態にならない")
    }
}
