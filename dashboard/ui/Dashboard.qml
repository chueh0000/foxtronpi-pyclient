import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: dashboardRoot
    // No anchors.fill: parent because StackView manages size

    Rectangle {
        anchors.fill: parent
        color: "#1e1e1e"

        GridLayout {
            anchors.fill: parent
            anchors.margins: 40
            columns: 3
            rows: 2
            rowSpacing: 40
            columnSpacing: 40

            // Speedometer Gauge
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10

                ColumnLayout {
                    anchors.centerIn: parent
                    Text {
                        text: "SPEED"
                        color: "#808080"
                        font.pixelSize: 20
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: vehicleManager.speed.toFixed(1)
                        color: "white"
                        font.pixelSize: 80
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: "km/h"
                        color: "#808080"
                        font.pixelSize: 20
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            // SOC Gauge
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10

                ColumnLayout {
                    anchors.centerIn: parent
                    Text {
                        text: "BATTERY"
                        color: "#808080"
                        font.pixelSize: 20
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: vehicleManager.hvBattSOC.toFixed(1) + "%"
                        color: vehicleManager.hvBattSOC < 20 ? "#F44336" : "#4CAF50"
                        font.pixelSize: 80
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: vehicleManager.hvBattTemp.toFixed(1) + "°C"
                        color: "#808080"
                        font.pixelSize: 20
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            // Steering Angle
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10

                ColumnLayout {
                    anchors.centerIn: parent
                    Text {
                        text: "STEERING"
                        color: "#808080"
                        font.pixelSize: 20
                        Layout.alignment: Qt.AlignHCenter
                    }
                    // Visual steering wheel
                    Rectangle {
                        width: 150
                        height: 150
                        radius: 75
                        color: "transparent"
                        border.color: "white"
                        border.width: 10
                        rotation: vehicleManager.sasAngle
                        
                        Rectangle {
                            width: 10
                            height: 75
                            color: "red"
                            anchors.top: parent.top
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                    Text {
                        text: vehicleManager.sasAngle.toFixed(1) + "°"
                        color: "white"
                        font.pixelSize: 30
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            // Pedals
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10
                Layout.columnSpan: 2

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 40
                    spacing: 60

                    // Brake Pedal
                    ColumnLayout {
                        Text { text: "BRAKE"; color: "white"; Layout.alignment: Qt.AlignHCenter }
                        Rectangle {
                            id: brakeBar
                            width: 50
                            height: 200
                            color: "#333"
                            radius: 5
                            Rectangle {
                                width: parent.width
                                height: parent.height * (vehicleManager.brakePedal / 100.0)
                                color: "#F44336"
                                radius: 5
                                anchors.bottom: parent.bottom
                            }
                        }
                    }

                    // Accel Pedal
                    ColumnLayout {
                        Text { text: "ACCEL"; color: "white"; Layout.alignment: Qt.AlignHCenter }
                        Rectangle {
                            id: accelBar
                            width: 50
                            height: 200
                            color: "#333"
                            radius: 5
                            Rectangle {
                                width: parent.width
                                height: parent.height * (vehicleManager.accelPedal / 100.0)
                                color: "#4CAF50"
                                radius: 5
                                anchors.bottom: parent.bottom
                            }
                        }
                    }
                }
            }
            
            // Lamp Status
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10
                
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 20
                    RowLayout {
                        spacing: 20
                        Rectangle { width: 40; height: 40; color: vehicleManager.pos_lamp ? "yellow" : "#333"; radius: 20 }
                        Rectangle { width: 40; height: 40; color: vehicleManager.low_beam ? "blue" : "#333"; radius: 20 }
                        Rectangle { width: 40; height: 40; color: vehicleManager.high_beam ? "cyan" : "#333"; radius: 20 }
                    }
                    RowLayout {
                        spacing: 20
                        Rectangle { width: 40; height: 40; color: vehicleManager.left_turn ? "orange" : "#333"; radius: 20 }
                        Rectangle { width: 40; height: 40; color: vehicleManager.right_turn ? "orange" : "#333"; radius: 20 }
                    }
                }
            }
        }
    }
}
