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
                    if let jsonData = buffer.data(using: .utf8), !buffer.isEmpty {
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
    @State private var modelName: String = "Vox AI Assistant"
    @State private var messageText: String = ""
    @State private var isConnecting: Bool = false
    @State private var errorMessage: String?
    @State private var showError: Bool = false
    @State private var isCapturingMedia: Bool = false
    @State private var capturedImage: UIImage?
    
    private let cameraCaptureManager = CameraCaptureManager()
    
    var body: some View {
        VStack {
            headerView()
            
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading) {
                        ForEach(messages) { message in
                            if message.isUser {
                                userChat(message)
                            } else {
                                assistantChat(message)
                            }
                        }
                        
                        if isConnecting {
                            HStack {
                                Spacer()
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .red))
                                Spacer()
                            }
                            .padding()
                            .id("loading")
                        }
                    }
                    .onChange(of: messages.count) { _ in
                        if let lastMessage = messages.last {
                            withAnimation {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                    .onChange(of: isConnecting) { _ in
                        if isConnecting {
                            withAnimation {
                                proxy.scrollTo("loading", anchor: .bottom)
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity)
                .clipped()
            }
            
            chatBar()
        }
        .background(backgroundView())
        .alert("Error", isPresented: $showError) {
            Button("OK") { showError = false }
        } message: {
            Text(errorMessage ?? "Unknown error occurred")
        }
        .sheet(isPresented: $isCapturingMedia) {
            if let capturedImage = capturedImage {
                VStack {
                    Image(uiImage: capturedImage)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxHeight: 300)
                    
                    HStack {
                        Button("Cancel") {
                            self.capturedImage = nil
                            isCapturingMedia = false
                        }
                        .padding()
                        
                        Spacer()
                        
                        Button("Send") {
                            if let imageData = capturedImage.jpegData(compressionQuality: 0.7) {
                                let base64String = imageData.base64EncodedString()
                                let imageID = "img\(Date().timeIntervalSince1970)"
                                sendImageMessage(imageID: imageID, base64Data: base64String)
                            }
                            self.capturedImage = nil
                            isCapturingMedia = false
                        }
                        .padding()
                    }
                }
                .padding()
            } else {
                Text("Capturing image...")
                    .onAppear {
                        captureImage()
                    }
            }
        }
    }
    
    private func headerView() -> some View {
        HStack {
            Button(action: { /* History button functionality */ }) {
                Image(systemName: "clock.arrow.circlepath")
                    .imageScale(.large)
                    .foregroundStyle(.white)
            }
            .padding(.horizontal, 20)
            
            Spacer()
            
            Text(modelName)
                .padding(.vertical, 20)
                .padding(.horizontal, 20)
                .foregroundStyle(.red.opacity(0.75))
                .font(.headline)
            
            Spacer()
            
            Button(action: { /* Info button functionality */ }) {
                Image(systemName: "info.circle")
                    .imageScale(.large)
                    .foregroundStyle(.white)
            }
            .padding(.horizontal, 20)
        }
    }
    
    private func userChat(_ message: Message) -> some View {
        HStack(spacing: 0) {
            Spacer()
            ZStack(alignment: .trailing) {
                VStack {
                    if let image = message.image {
                        Image(uiImage: image)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(maxWidth: 200, maxHeight: 200)
                            .cornerRadius(10)
                            .padding(.bottom, 8)
                    }
                    
                    Text(message.text)
                        .multilineTextAlignment(.leading)
                        .padding(12)
                        .foregroundStyle(.white)
                }
                .background {
                    RoundedRectangle(cornerRadius: 13, style: .continuous)
                        .fill(.red.opacity(0.25))
                        .frame(minWidth: 0, minHeight: 40)
                }
                .frame(maxWidth: 250)
            }
            .padding()
            .id(message.id)
        }
    }
    
    private func assistantChat(_ message: Message) -> some View {
        HStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 0) {
                Text(message.timestamp, style: .time)
                    .padding(.horizontal, 12)
                    .foregroundStyle(.secondary)
                    .font(.system(.caption))
                
                Text(message.text)
                    .multilineTextAlignment(.leading)
                    .padding(12)
                    .background {
                        RoundedRectangle(cornerRadius: 13, style: .continuous)
                            .fill(.black.opacity(0.25))
                    }
                    .foregroundStyle(.white)
            }
            .padding()
            .id(message.id)
            
            Spacer()
        }
    }
    
    private func chatBar() -> some View {
        HStack {
            Button(action: {
                isCapturingMedia = true
            }) {
                Image(systemName: "camera")
                    .symbolRenderingMode(.monochrome)
                    .padding(.vertical)
                    .padding(.horizontal, 5)
                    .foregroundStyle(.white)
            }
            
            Button(action: { /* Photo library functionality */ }) {
                Image(systemName: "photo")
                    .symbolRenderingMode(.monochrome)
                    .padding(.vertical)
                    .padding(.horizontal, 5)
                    .foregroundStyle(.white)
            }
            
            ZStack(alignment: .bottom) {
                RoundedRectangle(cornerRadius: 20)
                    .stroke(Color(.quaternaryLabel), lineWidth: 1)
                    .background(RoundedRectangle(cornerRadius: 20).fill(.red.opacity(0.33)))
                    .frame(height: 40)
                
                TextField(messageText.isEmpty ? "Message" : messageText, text: $messageText, onCommit: {
                    sendTextMessage()
                })
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .multilineTextAlignment(.leading)
                .foregroundStyle(.white)
            }
            .frame(height: 40)
            
            Button(action: {
                sendTextMessage()
            }) {
                Image(systemName: "paperplane")
                    .symbolRenderingMode(.monochrome)
                    .padding(.vertical)
                    .padding(.horizontal, 5)
                    .foregroundStyle(.white)
            }
            .disabled(messageText.isEmpty || isConnecting)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    private func backgroundView() -> some View {
        RoundedRectangle(cornerRadius: 4)
            .fill(.black)
    }
    
    private func captureImage() {
        cameraCaptureManager.startCapture { dataUri in
            if let dataUri = dataUri, let data = Data(base64Encoded: dataUri.components(separatedBy: ",")[1]) {
                DispatchQueue.main.async {
                    self.capturedImage = UIImage(data: data)
                }
            } else {
                DispatchQueue.main.async {
                    self.isCapturingMedia = false
                    self.errorMessage = "Failed to capture image"
                    self.showError = true
                }
            }
        }
    }
    
    func sendTextMessage() {
        guard !messageText.isEmpty && !isConnecting else { return }
        
        let text = messageText
        messageText = ""
        addUserMessage(text: text)
        
        receiveMessages(text)
    }
    
    func sendImageMessage(imageID: String, base64Data: String) {
        guard !isConnecting else { return }
        
        if let imageData = Data(base64Encoded: base64Data), let image = UIImage(data: imageData) {
            addUserMessage(text: "Sent image", image: image)
        } else {
            addUserMessage(text: "Sent image (preview not available)")
        }
        
        let images: [ImageData] = [
            ImageData(id: imageID, base64Data: base64Data)
        ]
        
        receiveMessages("Analyze this image", images: images)
    }
    
    func receiveMessages(_ messageText: String, images: [ImageData]? = nil) {
        isConnecting = true
        
        let request = NetworkManager.shared.createChatRequest(text: messageText, images: images)
        let assistantMessageId = addAssistantMessage("").id
        var fullMessageContent = ""
        
        let delegate = StreamDelegate()
        delegate.completion = { chatResponse in
            DispatchQueue.main.async {
                if let content = chatResponse.content {
                    fullMessageContent += content
                    
                    if let index = messages.firstIndex(where: { $0.id == assistantMessageId }) {
                        messages[index].text = fullMessageContent
                    }
                }
                
                if chatResponse.finishReason == "stop" || chatResponse.finishReason == "error" {
                    isConnecting = false
                }
            }
        }
        
        let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
        let task = session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    isConnecting = false
                    errorMessage = "Network error: \(error.localizedDescription)"
                    showError = true
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse, !(200...299).contains(httpResponse.statusCode) {
                    isConnecting = false
                    errorMessage = "Server error: \(httpResponse.statusCode)"
                    showError = true
                }
            }
        }
        
        task.resume()
    }
    
    func addUserMessage(text: String, image: UIImage? = nil) {
        let message = Message(id: UUID(), text: text, isUser: true, timestamp: Date(), image: image)
        messages.append(message)
    }
    
    func addAssistantMessage(_ text: String) -> Message {
        let message = Message(id: UUID(), text: text, isUser: false, timestamp: Date(), image: nil)
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

    enum CodingKeys: String, CodingKey {
        case id, model, created, index, role, content
        case finishReason = "finish_reason"
    }
}

struct Message: Identifiable {
    let id: UUID
    var text: String
    let isUser: Bool
    let timestamp: Date
    let image: UIImage?
}

#Preview {
    ChatView()
        .preferredColorScheme(.dark)
}

