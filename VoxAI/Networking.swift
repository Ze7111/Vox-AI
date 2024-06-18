//
//  Networking.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 6/16/24.
//

import Foundation

struct Networking {
    static func sendLoginRequest(serverIP: String, port: String, password: String, completion: @escaping (Result<Bool, Error>) -> Void) {
        // Placeholder for encryption and HTTP request logic
        
        // Example of URLSession request (not encrypted)
        guard let url = URL(string: "http://\(serverIP):\(port)/login") else {
            completion(.failure(NetworkingError.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: String] = ["password": password]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body, options: [])
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data, let response = response as? HTTPURLResponse, response.statusCode == 200 else {
                completion(.failure(NetworkingError.invalidResponse))
                return
            }
            
            // Handle response data
            completion(.success(true))
        }
        
        task.resume()
    }
    
    enum NetworkingError: Error {
        case invalidURL
        case invalidResponse
    }
}
