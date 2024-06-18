//
//  LandingPage.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 5/9/24.
//

import SwiftUI

struct LandingPage: View {
    @State private var selectedIndex: Int = 2
    @EnvironmentObject var appState: AppState
    
    private let symbols = [
        "square.2.layers.3d",
        "square.2.layers.3d.bottom.filled",
        "square.2.layers.3d.fill",
        "square.2.layers.3d.top.filled",
        "square.3.layers.3d.slash",
    ]
    
    var body: some View {
        VStack {
            // Top Image
            Image("LoginPage_LanderBanner")
                .renderingMode(.original)
                .resizable()
                .aspectRatio(contentMode: .fill)
                .frame(width: 356, height: 560)
                .clipped()
                .overlay(alignment: .topLeading) {
                    // Hero
                    VStack(alignment: .leading, spacing: 11) {
                        // App Icon
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
                        VStack(alignment: .leading, spacing: 1) {
                            Text("Vox AI")
                                .font(.system(.largeTitle, weight: .medium))
                                .foregroundColor(.white)
                            Text("A new way to transcend lectures.")
                                .font(.system(.headline, weight: .medium))
                                .frame(width: 190, alignment: .leading)
                                .clipped()
                                .multilineTextAlignment(.leading)
                                .foregroundColor(.white)
                        }
                    }
                    .padding()
                    .padding(.top, 42)
                }
                .overlay(alignment: .bottom) {
                    HStack {
                        ForEach(symbols.indices, id: \.self) { index in
                            Spacer()
                            
                            // Button to make each item selectable
                            Button(action: {
                                // Update the selected index when tapped
                                selectedIndex = index
                            }) {
                                // Update the icon's color based on the selection
                                Image(systemName: symbols[index])
                                    .symbolRenderingMode(.multicolor)
                                    .foregroundStyle(index == selectedIndex ? .red : .secondary)
                            }
                            
                            Spacer()
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .clipped()
                    .padding()
                    .background {
                        Rectangle()
                            .fill(.clear)
                            .background(Material.thin)
                            .mask {
                                RoundedRectangle(cornerRadius: 12, style: .continuous)
                            }
                    }
                    .padding()
                }
                .mask {
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                }
                .padding()
                .padding(.top, 40)
                .shadow(
                    color: Color(.sRGBLinear, red: 0 / 255, green: 0 / 255, blue: 0 / 255).opacity(
                        0.15), radius: 18, x: 0, y: 14
                )
                .blur(radius: 0)
            
            VStack(spacing: 10) {
                // "Login to Server" Button
                NavigationLink(destination: ChatView()) {
                    HStack(alignment: .firstTextBaseline) {
                        Image(systemName: "server.rack")
                            .imageScale(.medium)
                        Text("Login to Server")
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
                
                Text("Don't know what to do?")
                    .padding(.top)
                    .foregroundStyle(Color(.tertiaryLabel))
                    .font(.subheadline)
            }
            .padding(.horizontal)
            Spacer()
        }
    }
}

// Preview for Xcode canvas
#Preview {
    LandingPage()
        .environmentObject(AppState())
}
