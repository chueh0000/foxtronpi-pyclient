import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1280
    height: 800
    visible: true
    title: "FoxtronPi Real-time Dashboard"
    color: "#1e1e1e"

    // Error Dialog
    Dialog {
        id: errorDialog
        title: "Connection Error"
        standardButtons: Dialog.Ok
        anchors.centerIn: parent
        width: 400
        
        Text {
            id: errorText
            width: parent.width
            wrapMode: Text.WordWrap
            color: "white"
        }
        background: Rectangle {
            color: "#333333"
            border.color: "#F44336"
            border.width: 1
        }
    }

    Connections {
        target: vehicleManager
        function onConnectionError(msg) {
            errorText.text = msg;
            errorDialog.open();
        }
    }

    // Sidebar
    Rectangle {
        id: sidebar
        width: 200
        height: parent.height
        color: "#252526"

        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            anchors.topMargin: 20
            anchors.bottomMargin: 20

            // Navigation Buttons
            Button {
                text: "Dashboard"
                Layout.fillWidth: true
                onClicked: stackView.replace("Dashboard.qml")
            }
            Button {
                text: "Controls"
                Layout.fillWidth: true
                onClicked: stackView.replace("Controls.qml")
            }
            Button {
                text: "Plots"
                Layout.fillWidth: true
                onClicked: stackView.replace("Plots.qml")
            }

            Item { Layout.fillHeight: true } // Spacer

            // Connect Button
            Button {
                text: vehicleManager.connected ? "DISCONNECT" : "CONNECT VEHICLE"
                Layout.fillWidth: true
                Layout.margins: 10
                palette.button: vehicleManager.connected ? "#F44336" : "#2196F3"
                palette.buttonText: "white"
                font.bold: true
                onClicked: {
                    if (vehicleManager.connected) {
                        vehicleManager.disconnectVehicle()
                    } else {
                        vehicleManager.connectVehicle()
                    }
                }
            }

            // Connection Status
            Rectangle {
                Layout.fillWidth: true
                height: 40
                color: vehicleManager.connected ? "#4CAF50" : "#F44336"
                Text {
                    anchors.centerIn: parent
                    text: vehicleManager.connected ? "CONNECTED" : "DISCONNECTED"
                    color: "white"
                    font.bold: true
                }
            }
        }
    }

    // Main Content
    StackView {
        id: stackView
        anchors.left: sidebar.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        initialItem: "Dashboard.qml"
    }
}

