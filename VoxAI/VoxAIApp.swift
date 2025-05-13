//
//  VoxAIApp.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation
import SwiftUI

@main
struct VoxAIApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            MainView()
                .environmentObject(appState)
                .preferredColorScheme(.dark)
        }
    }
}

struct MainView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Group {
            if appState.isAuthenticated {
                ContentView()
            } else {
                LandingPage()
            }
        }
        .onAppear {
            // Check for existing credentials and try auto-login
            if let serverIP = UserDefaults.standard.string(forKey: "serverIP"),
               let port = UserDefaults.standard.string(forKey: "port"),
               let password = UserDefaults.standard.string(forKey: "password"),
               !serverIP.isEmpty && !port.isEmpty && !password.isEmpty {
                
                NetworkManager.shared.updateCredentials(serverIP: serverIP, port: port, password: password)
                NetworkManager.shared.sendLoginRequest { result in
                    DispatchQueue.main.async {
                        if case .success = result {
                            appState.isAuthenticated = true
                            appState.checkServerHealth()
                        }
                    }
                }
            }
        }
    }
}
