VoxAI/
├── App/
│   ├── Main.swift                          # entry point for the iOS app
│   ├── AppDelegate.swift                   # handles application lifecycle
│   ├── SceneDelegate.swift                 # manages app UI scenes
│   ├── Controllers/                        # view controllers for handling user interaction
│   │   ├── CameraViewController.swift      # controls camera input
│   │   ├── MicrophoneViewController.swift  # handles microphone input
│   │   └── ChatViewController.swift        # manages the chat interface
│   ├── Models/                             # data models
│   │   ├── User.swift
│   │   └── Message.swift
│   ├── Views/                              # custom views, including layout and styling
│   │   ├── InteractionView.swift
│   │   └── MessageCell.swift
│   ├── Utilities/                          # helper classes and utilities
│   │   ├── PermissionsManager.swift        # manages user permissions for camera and mic
│   │   └── AIProcessor.swift               # handles AI interactions
│   └── Assets.xcassets                     # image assets and icons
└── Server/
    ├── server.py                           # flask server handling backend processes
    ├── requirements.txt                    # python dependencies
    ├── ai/                                 # aI models and processing scripts
    │   ├── speech_recognition.py
    │   ├── image_processing.py
    │   └── model_loader.py
    └── utils/                              # utility scripts for server operations
        ├── logger.py
        └── config.py