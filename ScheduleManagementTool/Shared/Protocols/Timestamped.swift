import Foundation

protocol Timestamped {
    var id: UUID { get }
    var timestamp: Date { get set }
}
