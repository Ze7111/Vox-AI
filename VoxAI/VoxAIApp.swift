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
            NavigationView {
                ContentView()
                    .environmentObject(appState)
            }
        }
    }
}
