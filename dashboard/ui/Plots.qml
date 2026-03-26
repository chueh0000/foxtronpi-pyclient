import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: plotsRoot
    // No anchors.fill: parent because StackView manages size

    Rectangle {
        anchors.fill: parent
        color: "#1e1e1e"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 40

            Text {
                text: "Real-time Vehicle Metrics"
                color: "white"
                font.pixelSize: 32
                font.bold: true
            }

            // Speed Plot
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    Text { text: "VEHICLE SPEED (km/h)"; color: "#808080"; font.bold: true }
                    Canvas {
                        id: speedCanvas
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.clearRect(0, 0, width, height);
                            ctx.strokeStyle = "#4CAF50";
                            ctx.lineWidth = 2;
                            ctx.beginPath();
                            
                            var data = vehicleManager.speedBuffer;
                            var stepX = width / (data.length - 1);
                            var maxY = 200; // max 200 km/h
                            
                            for (var i = 0; i < data.length; i++) {
                                var x = i * stepX;
                                var y = height - (data[i] / maxY * height);
                                if (i == 0) ctx.moveTo(x, y);
                                else ctx.lineTo(x, y);
                            }
                            ctx.stroke();
                        }
                        Connections {
                            target: vehicleManager
                            function onDataUpdated() { speedCanvas.requestPaint(); }
                        }
                    }
                }
            }

            // SAS Plot
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#252526"
                radius: 10
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    Text { text: "STEERING ANGLE (deg)"; color: "#808080"; font.bold: true }
                    Canvas {
                        id: sasCanvas
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.clearRect(0, 0, width, height);
                            ctx.strokeStyle = "#2196F3";
                            ctx.lineWidth = 2;
                            ctx.beginPath();
                            
                            var data = vehicleManager.sasBuffer;
                            var stepX = width / (data.length - 1);
                            var rangeY = 1800; // -900 to 900
                            
                            for (var i = 0; i < data.length; i++) {
                                var x = i * stepX;
                                var y = height/2 - (data[i] / rangeY * height);
                                if (i == 0) ctx.moveTo(x, y);
                                else ctx.lineTo(x, y);
                            }
                            ctx.stroke();
                        }
                        Connections {
                            target: vehicleManager
                            function onDataUpdated() { sasCanvas.requestPaint(); }
                        }
                    }
                }
            }
        }
    }
}
