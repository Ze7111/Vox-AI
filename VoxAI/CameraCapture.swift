//
//  LoginPage.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 5/9/24.
//

import AVFoundation
import UIKit

class CameraCaptureManager: NSObject, AVCapturePhotoCaptureDelegate {
    private var captureSession: AVCaptureSession!
    private var photoOutput: AVCapturePhotoOutput!
    private var previewLayer: AVCaptureVideoPreviewLayer!
    private var completion: ((String?) -> Void)?

    override init() {
        super.init()
        setupCaptureSession()
    }

    private func setupCaptureSession() {
        captureSession = AVCaptureSession()
        captureSession.sessionPreset = .photo

        guard let backCamera = AVCaptureDevice.default(for: .video) else {
            print("No back camera available")
            return
        }

        do {
            let input = try AVCaptureDeviceInput(device: backCamera)
            if captureSession.canAddInput(input) {
                captureSession.addInput(input)
            }

            photoOutput = AVCapturePhotoOutput()
            if captureSession.canAddOutput(photoOutput) {
                captureSession.addOutput(photoOutput)
            }

            previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
            previewLayer.videoGravity = .resizeAspectFill

        } catch {
            print("Error setting up camera: \(error)")
        }
    }

    func startCapture(completion: @escaping (String?) -> Void) {
        self.completion = completion
        captureSession.startRunning()
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { // Simulate delay for capture
            self.capturePhoto()
        }
    }

    private func capturePhoto() {
        let settings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: settings, delegate: self)
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        captureSession.stopRunning()
        if let error = error {
            print("Error capturing photo: \(error)")
            completion?(nil)
            return
        }

        guard let imageData = photo.fileDataRepresentation() else {
            print("Error converting photo to data")
            completion?(nil)
            return
        }

        let base64Data = imageData.base64EncodedString()
        let dataUri = "data:image/png;base64,\(base64Data)"
        completion?(dataUri)
    }
}

// Usage:
// let cameraManager = CameraCaptureManager()
// cameraManager.startCapture { dataUri in
//     if let dataUri = dataUri {
//         print("Captured Image Data URI: \(dataUri)")
//     } else {
//         print("Failed to capture image")
//     }
// }