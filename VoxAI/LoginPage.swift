//
//  LoginPage.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation
import SwiftUI

struct LoginPage: View {
    @State private var serverIP: String = UserDefaults.standard.string(forKey: "serverIP") ?? "127.0.0.1"
    @State private var port: String = UserDefaults.standard.string(forKey: "port") ?? "6380"
    @State private var password: String = UserDefaults.standard.string(forKey: "password") ?? ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showError = false
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack {
            Spacer()

            RoundedRectangle(cornerRadius: 17, style: .continuous)
                .fill(.red)
                .frame(width: 72, height: 72)
                .clipped()
                .shadow(
                    color: Color(
                        .sRGBLinear, red: 0 / 255, green: 0 / 255, blue: 0 / 255
                    ).opacity(0.12), radius: 8, x: 0, y: 4
                )
                .overlay {
                    Image(
                        systemName:
                            "point.bottomleft.forward.to.arrowtriangle.uturn.scurvepath"
                    )
                    .imageScale(.large)
                    .symbolRenderingMode(.multicolor)
                    .font(.system(size: 31, weight: .regular, design: .default))
                    .foregroundColor(.black)
                }

            VStack(alignment: .center, spacing: 1) {
                Text("Vox AI")
                    .font(.system(.largeTitle, weight: .medium))
                    .foregroundColor(.white)
            }

            Spacer()

            VStack(alignment: .leading, spacing: 20) {
                CustomTextField(placeholder: "Server IP", text: $serverIP)
                CustomTextField(placeholder: "Port", text: $port)
                CustomSecureField(placeholder: "Password", text: $password)
            }
            .padding()

            Button(action: {
                loginToServer()
            }) {
                HStack(alignment: .firstTextBaseline) {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .red))
                            .scaleEffect(0.8)
                    } else {
                        Image(systemName: "server.rack")
                            .imageScale(.medium)
                        Text("Login")
                    }
                }
                .font(.system(.body, weight: .medium))
                .padding(.vertical, 16)
                .frame(maxWidth: .infinity)
                .clipped()
                .foregroundStyle(.red)
                .background {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .stroke(.clear.opacity(0.25), lineWidth: 0)
                        .background(
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(
                                .red.opacity(0.15)))
                }
            }
            .disabled(isLoading)
            .padding(.horizontal)

            Spacer()
        }
        .background(
            LinearGradient(
                gradient: Gradient(colors: [.red.opacity(0.3), .black.opacity(0.3)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .blur(radius: 100)
        )
        .padding()
        .alert("Connection Error", isPresented: $showError) {
            Button("OK") { showError = false }
        } message: {
            Text(errorMessage ?? "Unknown error")
        }
        .onAppear {
            // Pre-populate with stored values if available
            let storedIP = UserDefaults.standard.string(forKey: "serverIP")
            let storedPort = UserDefaults.standard.string(forKey: "port")
            let storedPassword = UserDefaults.standard.string(forKey: "password")
            
            if let storedIP = storedIP, !storedIP.isEmpty {
                serverIP = storedIP
            }
            
            if let storedPort = storedPort, !storedPort.isEmpty {
                port = storedPort
            }
            
            if let storedPassword = storedPassword, !storedPassword.isEmpty {
                password = storedPassword
                // Attempt auto-login if we have stored credentials
                loginToServer()
            }
        }
    }

    func loginToServer() {
        guard !isLoading else { return }
        
        isLoading = true
        errorMessage = nil
        
        // Update the network manager with current credentials
        NetworkManager.shared.updateCredentials(serverIP: serverIP, port: port, password: password)
        
        // Make HTTP request
        NetworkManager.shared.sendLoginRequest { result in
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success:
                    appState.isAuthenticated = true
                    
                case .failure(let error):
                    errorMessage = error.errorDescription
                    showError = true
                }
            }
        }
    }
}

struct CustomTextField: View {
    var placeholder: String
    @Binding var text: String
    
    var body: some View {
        ZStack(alignment: .leading) {
            if text.isEmpty {
                Text(placeholder)
                    .foregroundColor(.gray)
                    .padding(.leading, 15)
            }
            TextField(placeholder, text: $text)
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .stroke(Color.red.opacity(0.15), lineWidth: 1)
                        .background(
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(Color.black)
                        )
                )
                .foregroundColor(.white)
                .autocapitalization(.none)
                .disableAutocorrection(true)
        }
    }
}

struct CustomSecureField: View {
    var placeholder: String
    @Binding var text: String
    
    var body: some View {
        ZStack(alignment: .leading) {
            if text.isEmpty {
                Text(placeholder)
                    .foregroundColor(.gray)
                    .padding(.leading, 15)
            }
            SecureField(placeholder, text: $text)
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .stroke(Color.red.opacity(0.15), lineWidth: 1)
                        .background(
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(Color.black)
                        )
                )
                .foregroundColor(.white)
                .autocapitalization(.none)
                .disableAutocorrection(true)
        }
    }
}

#Preview {
    LoginPage()
        .environmentObject(AppState())
}
