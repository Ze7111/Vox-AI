//
//  AppState.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation
class AppState: ObservableObject {
    @Published var isAuthenticated: Bool = false
    
    init() {}
}
