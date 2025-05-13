//
//  ContentView.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 4/24/24.
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    @State private var showSettings = false
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Chat Tab
            NavigationView {
                ChatView()
                    .navigationBarTitle("Vox AI", displayMode: .inline)
                    .navigationBarItems(
                        leading: Button(action: {
                            appState.activeConversation = appState.startNewConversation()
                        }) {
                            Image(systemName: "plus")
                        },
                        trailing: Button(action: {
                            showSettings = true
                        }) {
                            Image(systemName: "gear")
                        }
                    )
            }
            .tabItem {
                Label("Chat", systemImage: "message.fill")
            }
            .tag(0)
            
            // History Tab
            NavigationView {
                ConversationHistoryView()
                    .navigationBarTitle("History", displayMode: .inline)
            }
            .tabItem {
                Label("History", systemImage: "clock.fill")
            }
            .tag(1)
            
            // Settings Tab
            NavigationView {
                SettingsView()
                    .navigationBarTitle("Settings", displayMode: .inline)
            }
            .tabItem {
                Label("Settings", systemImage: "gear")
            }
            .tag(2)
        }
        .accentColor(.red)
        .overlay(
            serverStatusOverlay
                .animation(.easeInOut, value: appState.serverStatus)
        )
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
    }
    
    @ViewBuilder
    private var serverStatusOverlay: some View {
        if appState.serverStatus != .ready {
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    VStack(spacing: 8) {
                        if appState.serverStatus == .initializing {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .red))
                        }
                        Text("Server Status: \(appState.serverStatus.rawValue)")
                            .font(.footnote)
                            .foregroundColor(.white)
                    }
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(10)
                    .padding()
                    Spacer()
                }
            }
        }
    }
}

struct ConversationHistoryView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        List {
            if appState.conversationHistory.isEmpty {
                Text("No conversation history")
                    .foregroundColor(.gray)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .center)
            } else {
                ForEach(appState.conversationHistory) { conversation in
                    Button(action: {
                        appState.activeConversation = conversation.id
                    }) {
                        ConversationRow(conversation: conversation)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                .onDelete { indexSet in
                    appState.conversationHistory.remove(atOffsets: indexSet)
                }
            }
        }
        .listStyle(InsetGroupedListStyle())
    }
}

struct ConversationRow: View {
    let conversation: ConversationSummary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(conversation.title)
                .font(.headline)
                .foregroundColor(.primary)
            
            if !conversation.lastMessagePreview.isEmpty {
                Text(conversation.lastMessagePreview)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            
            HStack {
                Text(conversation.timestamp, style: .relative)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text("\(conversation.messageCount) \(conversation.messageCount == 1 ? "message" : "messages")")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var serverIP: String = UserDefaults.standard.string(forKey: "serverIP") ?? "127.0.0.1"
    @State private var port: String = UserDefaults.standard.string(forKey: "port") ?? "6380"
    @State private var password: String = UserDefaults.standard.string(forKey: "password") ?? ""
    @State private var showingLogoutConfirmation = false
    @State private var showingReconnectAlert = false
    
    var body: some View {
        Form {
            Section(header: Text("Server Configuration")) {
                TextField("Server IP", text: $serverIP)
                    .keyboardType(.numbersAndPunctuation)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                
                TextField("Port", text: $port)
                    .keyboardType(.numberPad)
                
                SecureField("Password", text: $password)
                
                Button(action: {
                    NetworkManager.shared.updateCredentials(serverIP: serverIP, port: port, password: password)
                    showingReconnectAlert = true
                }) {
                    Text("Save and Reconnect")
                        .foregroundColor(.red)
                }
                .alert(isPresented: $showingReconnectAlert) {
                    Alert(
                        title: Text("Reconnecting"),
                        message: Text("Attempting to reconnect to the server..."),
                        dismissButton: .default(Text("OK"))
                    )
                }
            }
            
            Section {
                Button(action: {
                    showingLogoutConfirmation = true
                }) {
                    Text("Logout")
                        .foregroundColor(.red)
                }
                .alert(isPresented: $showingLogoutConfirmation) {
                    Alert(
                        title: Text("Logout Confirmation"),
                        message: Text("Are you sure you want to logout?"),
                        primaryButton: .destructive(Text("Logout")) {
                            appState.logout()
                        },
                        secondaryButton: .cancel()
                    )
                }
            }
            
            Section(header: Text("About")) {
                HStack {
                    Text("Version")
                    Spacer()
                    Text("1.0.0")
                        .foregroundColor(.gray)
                }
                
                HStack {
                    Text("Build")
                    Spacer()
                    Text("2024.05.12")
                        .foregroundColor(.gray)
                }
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
