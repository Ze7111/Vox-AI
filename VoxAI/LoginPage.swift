//
//  LoginPage.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation
import SwiftUI

struct LoginPage: View {
    @State private var serverIP: String = ""
    @State private var port: String = ""
    @State private var password: String = ""
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
                CustomTextField(placeholder:   "Server IP", text: $serverIP)
                CustomTextField(placeholder:   "Port", text: $port)
                CustomSecureField(placeholder: "Password", text: $password)
            }
            .padding()

            Button(action: {
                loginToServer()
            }) {
                HStack(alignment: .firstTextBaseline) {
                    Image(systemName: "server.rack")
                        .imageScale(.medium)
                    Text("Login")
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
    }

    func loginToServer() {
        // Placeholder for login logic
        // Save credentials to UserDefaults
        UserDefaults.standard.set(serverIP, forKey: "serverIP")
        UserDefaults.standard.set(port, forKey: "port")
        UserDefaults.standard.set(password, forKey: "password")

        // Make encrypted HTTP request
        Networking.sendLoginRequest(serverIP: serverIP, port: port, password: password) { result in
            switch result {
            case .success(let success):
                if success {
                    DispatchQueue.main.async {
                        appState.isAuthenticated = true
                    }
                }
            case .failure(let error):
                print("Login failed: \(error.localizedDescription)")
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
        }
    }
}

// Preview for Xcode canvas
#Preview {
    LoginPage()
        .environmentObject(AppState())
}
