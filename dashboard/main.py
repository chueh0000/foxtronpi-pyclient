import os
import sys

# Add the parent directory to the Python path to access root modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend.vehicle_manager import VehicleManager

def main():
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("Foxtron")
    app.setOrganizationDomain("foxtron.com")
    app.setApplicationName("FoxtronPi Dashboard")

    engine = QQmlApplicationEngine()
    
    # Instantiate the backend without pre-loading x86_64 modules
    vehicle_manager = VehicleManager()
    
    # Register the backend object to QML context
    engine.rootContext().setContextProperty("vehicleManager", vehicle_manager)

    # Load the main QML file
    qml_file = os.path.join(os.path.dirname(__file__), "ui", "main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
