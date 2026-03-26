import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: controlsRoot
    // No anchors.fill: parent because StackView manages size

    Flickable {
        anchors.fill: parent
        contentHeight: column.height + 80
        clip: true

        ColumnLayout {
            id: column
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 40
            spacing: 30

            Text {
                text: "Vehicle Controls"
                color: "white"
                font.pixelSize: 32
                font.bold: true
            }

            // Quick Actions
            RowLayout {
                spacing: 20
                Button {
                    text: "RESET SEQUENCE"
                    onClicked: vehicleManager.resetSequence()
                }
                Button {
                    text: "CTRL ENABLE"
                    onClicked: vehicleManager.setCtrlEnableSwitch(new Array(1).fill(1))
                }
                Button {
                    text: "CTRL DISABLE"
                    onClicked: vehicleManager.setDrivingCtrl(new Array(1).fill(0))
                }
            }

            // Driving Controls (Group 1001)
            Rectangle {
                Layout.fillWidth: true
                height: drivingGrid.height + 60
                color: "#252526"
                radius: 10
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    Text { text: "Driving Control (DID 0x1001)"; color: "#808080"; font.bold: true }
                    
                    GridLayout {
                        id: drivingGrid
                        columns: 4
                        columnSpacing: 20
                        rowSpacing: 10
                        
                        // Just a few examples to keep it concise, but in a real app all 14 would be here
                        Label { text: "AccReq (-15 to 15)"; color: "white" }
                        SpinBox { id: accReq; from: -1500; to: 1500; value: 0; stepSize: 5 } // factor 0.05
                        
                        Label { text: "TargetSpd (0 to 255)"; color: "white" }
                        SpinBox { id: targetSpd; from: 0; to: 255; value: 0 }
                        
                        Label { text: "AngleTarget (-900 to 900)"; color: "white" }
                        SpinBox { id: angleTarget; from: -9000; to: 9000; value: 0; stepSize: 10 } // factor 0.1
                        
                        Button {
                            text: "SEND DRIVING CTRL"
                            Layout.columnSpan: 4
                            onClicked: {
                                var vals = [
                                    accReq.value / 100.0, 1, // Acc, Acc_A
                                    targetSpd.value, 1,    // Spd, Spd_A
                                    1, 1,                  // Angle_V, Angle_Req
                                    angleTarget.value / 10.0, // Angle
                                    1, 1, 0,               // Torque_V, Torque_Req, Torque
                                    0, 0, 0, 0             // APS stuff
                                ]
                                vehicleManager.setDrivingCtrl(vals)
                            }
                        }
                    }
                }
            }

            // Lamp Controls (Group 100C)
            Rectangle {
                Layout.fillWidth: true
                height: lampGrid.height + 60
                color: "#252526"
                radius: 10
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    Text { text: "Lamp Control (DID 0x100C)"; color: "#808080"; font.bold: true }
                    
                    GridLayout {
                        id: lampGrid
                        columns: 4
                        columnSpacing: 20
                        
                        Switch { id: posLampEn; text: "Pos Lamp En"; palette.windowText: "white" }
                        Switch { id: posLamp; text: "Pos Lamp State"; palette.windowText: "white" }
                        
                        Switch { id: lowBeamEn; text: "Low Beam En"; palette.windowText: "white" }
                        Switch { id: lowBeam; text: "Low Beam State"; palette.windowText: "white" }

                        Button {
                            text: "SEND LAMP CTRL"
                            Layout.columnSpan: 4
                            onClicked: {
                                var vals = new Array(25).fill(0)
                                vals[0] = posLampEn.checked ? 1 : 0
                                vals[1] = posLamp.checked ? 1 : 0
                                vals[2] = lowBeamEn.checked ? 1 : 0
                                vals[3] = lowBeam.checked ? 1 : 0
                                // ... Fill the rest
                                vehicleManager.setLamps(vals)
                            }
                        }
                    }
                }
            }
        }
    }
}
