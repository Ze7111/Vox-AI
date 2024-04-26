//
//  ContentView.swift
//  VoxAI
//
//  Created by Dhruvan Kartik on 4/24/24.
//

import SwiftUI
import RealityKit
import ARKit
import Combine

struct ContentView : View {
    var body: some View {
        ARViewContainer().edgesIgnoringSafeArea(.all)
    }
    
}

struct ARViewContainer: UIViewRepresentable {
    
    func makeUIView(context: Context) -> CustomARView {
        return CustomARView()
    }
    
    
    
    func updateUIView(_ uiView: CustomARView, context: Context) {}
}

// Define a custom ARView class that setups the AR scene with occlusion
class CustomARView: ARView {
    
    init() {
        super.init(frame: .zero)
        setupARView()
        setupGesture()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    @MainActor required dynamic init(frame frameRect: CGRect) {
        fatalError("init(frame:) has not been implemented")
    }
    
    
    
    private func setupARView() {
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        if ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) {
            configuration.sceneReconstruction = .mesh
        }
        configuration.environmentTexturing = .automatic
        configuration.frameSemantics.insert(.sceneDepth)

        // Reduce the complexity of the AR configuration to optimize performance
        configuration.isLightEstimationEnabled = false  // Disable if not needed
        self.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])

        
        self.environment.sceneUnderstanding.options.insert(.occlusion)
        self.environment.sceneUnderstanding.options.insert(.collision)
        self.environment.sceneUnderstanding.options.insert(.receivesLighting)
    }


    private func setupGesture() {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        self.addGestureRecognizer(tapGesture)
    }
        
    @objc func handleTap(_ sender: UITapGestureRecognizer) {
        let location = sender.location(in: self)
        print("Tap location: \(location)")

        if let raycastQuery = self.makeRaycastQuery(from: location, allowing: .estimatedPlane, alignment: .any) {
            let results = self.session.raycast(raycastQuery)
            print("Raycast results count: \(results.count)")
            if let firstResult = results.first {
                DispatchQueue.main.async {
                    print("Placing object at \(firstResult.worldTransform.columns.3)")
                    self.placeObject(at: firstResult)
                }
            } else {
                print("No surface found at tap location")
            }
        } else {
            print("No raycast query could be made")
        }
    }
    
    private func placeObject(at raycastResult: ARRaycastResult) {
        // Create a cube model
        let mesh = MeshResource.generateBox(size: 0.1, cornerRadius: 0.005)
        let material = SimpleMaterial(color: .gray, roughness: 0.15, isMetallic: true)
        let model = ModelEntity(mesh: mesh, materials: [material])
        model.transform.translation.y = 0.05
        //model.transform.matrix = raycastResult.worldTransform

        if let anchor = raycastResult.anchor {
            let planeAnchor = AnchorEntity(anchor: anchor)
            planeAnchor.addChild(model)
            self.scene.addAnchor(planeAnchor)
            print("auto")
        } else {
            // If no anchor is associated with the raycast result, create a manual anchor at the position
            let manualAnchor = AnchorEntity(world: raycastResult.worldTransform)
            manualAnchor.addChild(model)
            self.scene.addAnchor(manualAnchor)
            
           
            print("man")
        }
    }
}


#Preview {
    ContentView()
}
