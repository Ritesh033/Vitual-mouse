from setuptools import find_packages, setup

setup(
    name="GestureOS",
    version="0.1.0",
    description="A gesture-driven desktop control platform.",
    packages=find_packages(exclude=["tests*", "docs*"]),
    install_requires=[
        "opencv-python>=4.8.1",
        "mediapipe==0.10.9",
        "numpy>=1.24.3",
        "pyautogui>=0.9.53",
        "pynput>=1.7.6",
        "tensorflow>=2.15.0",
        "torch>=2.1.1",
        "torchaudio>=2.1.1",
        "PyYAML>=6.0.1",
        "Pillow>=10.4.0",
        "SpeechRecognition>=3.10.0",
        "pyttsx3>=2.90",
    ],
)
