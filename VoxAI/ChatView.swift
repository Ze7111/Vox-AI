//
//  ChatView.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/17/24.
//

import Foundation
import SwiftUI

class StreamDelegate: NSObject, URLSessionDataDelegate {
    var buffer = ""
    var completion: ((ChatResponse) -> Void)?
    
    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        if let stringData = String(data: data, encoding: .utf8) {
            for character in stringData {
                if character == "\n" {
                    if let jsonData = buffer.data(using: .utf8) {
                        do {
                            let chatResponse = try JSONDecoder().decode(ChatResponse.self, from: jsonData)
                            completion?(chatResponse)
                        } catch {
                            print("Error decoding JSON: \(error)")
                        }
                    }
                    buffer = ""
                } else {
                    buffer.append(character)
                }
            }
        }
    }
}

struct ChatView: View {
    @State private var messages: [Message] = []
    @State private var modelName: String = "Boolean Algebra"
    @State private var messageText: String = ""
    
    var body: some View {
        VStack {
            headerView()
            Spacer()
            ScrollView {
                VStack(alignment: .leading) {
                    ForEach(messages) { message in
                        if message.isUser {
                            userChat(message.text)
                        } else {
                            assistantChat(message.text)
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity)
            .clipped()
            Spacer()
            chatBar()
        }
        .background(backgroundView())
    }
    
    private func headerView() -> some View {
        HStack {
            chatBarButton(systemName: "clock.arrow.circlepath", action: { print("History Clicked") })
                .padding(.horizontal, 20)
            Spacer()
            Text(modelName)
                .padding(.vertical, 20)
                .padding(.horizontal, 20)
                .foregroundStyle(.red.opacity(0.75))
            Spacer()
            chatBarButton(systemName: "info.circle", action: { print("Info Clicked") })
                .padding(.horizontal, 20)
        }
    }
    
    private func userChat(_ text: String) -> some View {
        HStack(spacing: 0) {
            Spacer()
            ZStack(alignment: .trailing) {
                Text(text)
                    .multilineTextAlignment(.leading)
                    .padding(12)
                    .frame(alignment: .center)
                    .clipped()
                    .background {
                        RoundedRectangle(cornerRadius: 13, style: .continuous)
                            .fill(.red.opacity(0.25))
                            .frame(minWidth: 0, minHeight: 40, alignment: .trailing)
                            .clipped()
                            .padding(0)
                            .frame(maxWidth: 250, alignment: .trailing)
                            .clipped()
                    }
                    .foregroundStyle(.white)
            }
            .frame(maxWidth: 250, alignment: .trailing)
            .clipped()
            .frame(minHeight: 70)
            .clipped()
        }
        .frame(minHeight: 80, alignment: .trailing)
        .clipped()
        .padding()
    }
    
    private func assistantChat(_ text: String) -> some View {
        HStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 0) {
                Text(Date(), style: .time)
                    .padding(.horizontal, 12)
                    .foregroundStyle(.secondary)
                    .font(.system(.caption))
                ZStack(alignment: .leading) {
                    Text(text)
                        .multilineTextAlignment(.leading)
                        .padding(12)
                        .frame(alignment: .center)
                        .clipped()
                        .background {
                            RoundedRectangle(cornerRadius: 13, style: .continuous)
                                .fill(.black.opacity(0.25))
                                .frame(minWidth: 0, minHeight: 40, alignment: .trailing)
                                .clipped()
                                .padding(0)
                        }
                        .foregroundStyle(.white)
                }
                .frame(minHeight: 70)
                .clipped()
            }
        }
        .frame(minHeight: 80, alignment: .leading)
        .clipped()
        .padding()
    }
    
    private func chatBar() -> some View {
        HStack {
            chatBarButton(systemName: "camera", action: { print("Camera button clicked") })
            chatBarButton(systemName: "photo", action: { print("Photo button clicked") })
            chatBarButton(systemName: "mic", action: { print("Mic button clicked") })
            ZStack(alignment: .bottom) {
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(Color(.quaternaryLabel), lineWidth: 1)
                    .background(RoundedRectangle(cornerRadius: 20, style: .continuous).fill(.red.opacity(0.33)))
                    .overlay {
                        TextField(messageText.isEmpty ? "Message" : messageText, text: $messageText, onCommit: {
                            onMessageSend(messageText)
                        })
                            .padding()
                            .multilineTextAlignment(.leading)
                            .foregroundStyle(Color(.tertiaryLabel))
                            .background(Material.thick)
                            .mask { RoundedRectangle(cornerRadius: 40, style: .continuous) }
                    }
            }
            .frame(width: 185, height: 35)
            .clipped()
            .padding(.vertical)
            .padding(.horizontal, 5)
            chatBarButton(systemName: "paperplane", action: { onMessageSend(messageText) })
        }
    }
    
    private func chatBarButton(systemName: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .symbolRenderingMode(.monochrome)
                .padding(.vertical)
                .padding(.horizontal, 5)
                .foregroundStyle(.white)
        }
    }
    
    private func backgroundView() -> some View {
        RoundedRectangle(cornerRadius: 4, style: .continuous)
            .fill(.black)
        
        // ZStack {
        //     RoundedRectangle(cornerRadius: 4, style: .continuous)
        //         .fill(.black)
        //     LinearGradient(gradient: Gradient(colors: [.black, .purple.opacity(0.33), .indigo.opacity(0.33), .black]), startPoint: .top, endPoint: .bottom)
        //     Rectangle()
        //         .fill(.clear)
        //         .background(Material.ultraThick)
        // }
    }

    func receiveMessages(_ messageText: String, completion: @escaping (ChatResponse) -> Void) {
        guard let url = URL(string: "http://192.168.0.135:6380/chat") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any?] = [
            "text": messageText,
            "top_k": 40,
            "top_p": 1.0,
            "min_p": 0.0,
            "temperature": 0.7,
            "seed": 0,
            "images": nil
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody, options: [])
        } catch {
            print("Error serializing JSON: \(error)")
            return
        }
        
        let delegate = StreamDelegate()
        delegate.completion = completion
        let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
        let task = session.dataTask(with: request)
        
        task.resume()
    }

    func onMessageSend(_ text: String) {
        addUserMessage(text)
        messageText = ""

        let assistantMessageId = addAssistantMessage("").id
        var fullMessageContent = ""

        receiveMessages(text) { chatResponse in
            DispatchQueue.main.async {
                if let content = chatResponse.content {
                    fullMessageContent += content

                    if let index = messages.firstIndex(where: { $0.id == assistantMessageId }) {
                        messages[index].text += content
                    }
                }
            }
        }
    }
    
    func addUserMessage(_ text: String) {
        let message = Message(id: UUID(), text: text, isUser: true)
        messages.append(message)
    }

    // add a assistant message that returns a reference to the message so it can be edited as the model streams back data
    func addAssistantMessage(_ text: String) -> Message {
        let message = Message(id: UUID(), text: text, isUser: false)
        messages.append(message)
        return message
    }
    
    func setModelName(_ name: String) {
        modelName = name
    }
}

struct ChatResponse: Decodable {
    let id: String
    let model: String
    let created: Int
    let index: Int
    let role: String?
    let content: String?
    let finishReason: String?

    private enum CodingKeys: String, CodingKey {
        case id, model, created, index, role, content, finishReason = "finish_reason"
    }
}

struct Message: Identifiable {
    let id: UUID
    var text: String
    let isUser: Bool
}

// Preview for Xcode canvas
#Preview {
    ChatView()
        .preferredColorScheme(.dark)
}

