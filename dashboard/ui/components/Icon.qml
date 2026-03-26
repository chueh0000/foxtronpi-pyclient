import QtQuick

Text {
    id: root
    font.family: "FontAwesome"
    font.pixelSize: 24
    color: "white"
    
    // Some common icons (mapping unicode)
    readonly property string icon_speed: "\uf0e4"
    readonly property string icon_battery: "\uf240"
    readonly property string icon_steering: "\uf14e"
    readonly property string icon_light: "\uf0eb"
    readonly property string icon_settings: "\uf013"
}
