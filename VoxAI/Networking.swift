//
//  Networking.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    private var serverIP: String = UserDefaults.standard.string(forKey: "serverIP") ?? "127.0.0.1"
    private var port: String = UserDefaults.standard.string(forKey: "port") ?? "6380"
    private var password: String = UserDefaults.standard.string(forKey: "password") ?? ""
    
    private init() {}
    
    func updateCredentials(serverIP: String, port: String, password: String) {
        self.serverIP = serverIP
        self.port = port
        self.password = password
        
        UserDefaults.standard.set(serverIP, forKey: "serverIP")
        UserDefaults.standard.set(port, forKey: "port")
        UserDefaults.standard.set(password, forKey: "password")
    }
    
    func getBaseURL() -> String {
        return "http://\(serverIP):\(port)"
    }
    
    func getAuthHeader() -> String {
        let loginString = "admin:\(password)"
        let loginData = loginString.data(using: .utf8)!
        return "Basic \(loginData.base64EncodedString())"
    }
    
    func sendLoginRequest(completion: @escaping (Result<Bool, NetworkingError>) -> Void) {
        guard let url = URL(string: "\(getBaseURL())/login") else {
            completion(.failure(.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(getAuthHeader(), forHTTPHeaderField: "Authorization")
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(.connectionError(error)))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(.invalidResponse))
                return
            }
            
            switch httpResponse.statusCode {
            case 200...299:
                completion(.success(true))
            case 401:
                completion(.failure(.unauthorized))
            case 503:
                completion(.failure(.serviceUnavailable))
            default:
                completion(.failure(.serverError(httpResponse.statusCode)))
            }
        }
        
        task.resume()
    }
    
    func checkServerHealth(completion: @escaping (Result<ServerHealth, NetworkingError>) -> Void) {
        guard let url = URL(string: "\(getBaseURL())/health") else {
            completion(.failure(.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(.connectionError(error)))
                return
            }
            
            guard let data = data else {
                completion(.failure(.noData))
                return
            }
            
            do {
                let health = try JSONDecoder().decode(ServerHealth.self, from: data)
                completion(.success(health))
            } catch {
                completion(.failure(.decodingError(error)))
            }
        }
        
        task.resume()
    }
    
    func createChatRequest(text: String, images: [ImageData]? = nil) -> URLRequest {
        guard let url = URL(string: "\(getBaseURL())/chat") else {
            fatalError("Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(getAuthHeader(), forHTTPHeaderField: "Authorization")
        
        let requestBody: [String: Any?] = [
            "text": text,
            "top_k": 40,
            "top_p": 0.9,
            "min_p": 0.05,
            "temperature": 0.7,
            "seed": Int.random(in: 1..<1000),
            "images": images?.map { ["img_id": $0.id, "base64_img": $0.base64Data] }
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody.compactMapValues { $0 })
        } catch {
            print("Error serializing chat request: \(error)")
        }
        
        return request
    }
}

struct ServerHealth: Codable {
    let status: String
    let modelLoaded: Bool
    let version: String
    
    enum CodingKeys: String, CodingKey {
        case status
        case modelLoaded = "model_loaded"
        case version
    }
}

struct ImageData {
    let id: String
    let base64Data: String
}

enum NetworkingError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case noData
    case unauthorized
    case connectionError(Error)
    case decodingError(Error)
    case serverError(Int)
    case serviceUnavailable
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid server URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .noData:
            return "No data received from server"
        case .unauthorized:
            return "Incorrect username or password"
        case .connectionError(let error):
            return "Connection error: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Data decoding error: \(error.localizedDescription)"
        case .serverError(let code):
            return "Server error with code: \(code)"
        case .serviceUnavailable:
            return "Service temporarily unavailable"
        }
    }
}
