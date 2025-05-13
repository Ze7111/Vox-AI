//
//  LoginPage.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 5/9/24.
//

import AVFoundation
import UIKit

enum CameraCaptureError: Error {
    case cameraUnavailable
    case permissionDenied
    case setupFailed(Error)
    case captureFailed
    case processingFailed(Error)
}

class CameraCaptureManager: NSObject, AVCapturePhotoCaptureDelegate {
    private var captureSession: AVCaptureSession?
    private var photoOutput: AVCapturePhotoOutput?
    private var previewLayer: AVCaptureVideoPreviewLayer?
    private var completion: ((String?, CameraCaptureError?) -> Void)?
    
    private var isConfigured = false
    
    override init() {
        super.init()
    }
    
    func checkPermissions(completion: @escaping (Bool) -> Void) {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            completion(true)
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async {
                    completion(granted)
                }
            }
        case .denied, .restricted:
            completion(false)
        @unknown default:
            completion(false)
        }
    }
    
    private func setupCaptureSession() -> Result<Void, CameraCaptureError> {
        let session = AVCaptureSession()
        session.sessionPreset = .photo
        
        guard let backCamera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) else {
            return .failure(.cameraUnavailable)
        }
        
        do {
            let input = try AVCaptureDeviceInput(device: backCamera)
            if session.canAddInput(input) {
                session.addInput(input)
            } else {
                return .failure(.setupFailed(NSError(domain: "CameraCaptureManager", code: 1, userInfo: [NSLocalizedDescriptionKey: "Could not add camera input"])))
            }
            
            let output = AVCapturePhotoOutput()
            if session.canAddOutput(output) {
                session.addOutput(output)
                self.photoOutput = output
            } else {
                return .failure(.setupFailed(NSError(domain: "CameraCaptureManager", code: 2, userInfo: [NSLocalizedDescriptionKey: "Could not add photo output"])))
            }
            
            self.captureSession = session
            self.isConfigured = true
            return .success(())
        } catch {
            return .failure(.setupFailed(error))
        }
    }
    
    func startCapture(completion: @escaping (String?, CameraCaptureError?) -> Void) {
        self.completion = completion
        
        checkPermissions { [weak self] granted in
            guard let self = self else { return }
            
            if !granted {
                completion(nil, .permissionDenied)
                return
            }
            
            if !self.isConfigured {
                let result = self.setupCaptureSession()
                if case .failure(let error) = result {
                    completion(nil, error)
                    return
                }
            }
            
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                guard let self = self, let captureSession = self.captureSession else {
                    DispatchQueue.main.async {
                        completion(nil, .setupFailed(NSError(domain: "CameraCaptureManager", code: 3, userInfo: [NSLocalizedDescriptionKey: "Session not configured"])))
                    }
                    return
                }
                
                captureSession.startRunning()
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                    self?.capturePhoto()
                }
            }
        }
    }
    
    private func capturePhoto() {
        guard let photoOutput = self.photoOutput else {
            completion?(nil, .captureFailed)
            return
        }
        
        let settings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: settings, delegate: self)
    }
    
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self, let captureSession = self.captureSession else { return }
            
            captureSession.stopRunning()
            
            if let error = error {
                DispatchQueue.main.async {
                    self.completion?(nil, .processingFailed(error))
                }
                return
            }
            
            guard let imageData = photo.fileDataRepresentation() else {
                DispatchQueue.main.async {
                    self.completion?(nil, .processingFailed(NSError(domain: "CameraCaptureManager", code: 4, userInfo: [NSLocalizedDescriptionKey: "Could not get image data"])))
                }
                return
            }
            
            let base64Data = imageData.base64EncodedString()
            let dataUri = "data:image/jpeg;base64,\(base64Data)"
            
            DispatchQueue.main.async {
                self.completion?(dataUri, nil)
            }
        }
    }
    
    deinit {
        captureSession?.stopRunning()
    }
}