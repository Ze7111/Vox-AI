//
//  AppState.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation
import SwiftUI
import Combine

class AppState: ObservableObject {
    @Published var isAuthenticated: Bool = false
    @Published var isServerConnected: Bool = false
    @Published var activeConversation: String? = nil
    @Published var conversationHistory: [ConversationSummary] = []
    @Published var serverStatus: ServerStatus = .unknown
    
    private var cancellables = Set<AnyCancellable>()
    private let healthCheckTimer: Timer?
    
    init() {
        healthCheckTimer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { [weak self] _ in
            self?.checkServerHealth()
        }
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.willEnterForegroundNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.checkServerHealth()
        }
    }
    
    deinit {
        healthCheckTimer?.invalidate()
        NotificationCenter.default.removeObserver(self)
    }
    
    func checkServerHealth() {
        guard isAuthenticated else { return }
        
        NetworkManager.shared.checkServerHealth { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let health):
                    self?.isServerConnected = health.modelLoaded
                    self?.serverStatus = health.modelLoaded ? .ready : .initializing
                case .failure:
                    self?.isServerConnected = false
                    self?.serverStatus = .disconnected
                }
            }
        }
    }
    
    func logout() {
        isAuthenticated = false
        isServerConnected = false
        serverStatus = .unknown
    }
    
    func startNewConversation() -> String {
        let id = UUID().uuidString
        let summary = ConversationSummary(
            id: id,
            title: "New Conversation",
            lastMessagePreview: "",
            timestamp: Date(),
            messageCount: 0
        )
        conversationHistory.insert(summary, at: 0)
        activeConversation = id
        return id
    }
    
    func updateConversationTitle(_ id: String, newTitle: String) {
        if let index = conversationHistory.firstIndex(where: { $0.id == id }) {
            conversationHistory[index].title = newTitle
        }
    }
    
    func updateConversation(_ id: String, withMessage message: String, isUser: Bool) {
        if let index = conversationHistory.firstIndex(where: { $0.id == id }) {
            conversationHistory[index].lastMessagePreview = message.prefix(50) + (message.count > 50 ? "..." : "")
            conversationHistory[index].timestamp = Date()
            conversationHistory[index].messageCount += 1
            
            // Move conversation to top of list
            if index > 0 {
                let conversation = conversationHistory.remove(at: index)
                conversationHistory.insert(conversation, at: 0)
            }
        }
    }
}

enum ServerStatus: String {
    case unknown = "Unknown"
    case disconnected = "Disconnected"
    case initializing = "Initializing"
    case ready = "Ready"
}

struct ConversationSummary: Identifiable, Equatable {
    let id: String
    var title: String
    var lastMessagePreview: String
    var timestamp: Date
    var messageCount: Int
    
    static func == (lhs: ConversationSummary, rhs: ConversationSummary) -> Bool {
        lhs.id == rhs.id
    }
}
