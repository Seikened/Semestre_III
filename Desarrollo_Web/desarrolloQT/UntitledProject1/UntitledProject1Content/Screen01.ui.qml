

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 6.5
import QtQuick.Controls 6.5
import UntitledProject1
import QtQuick.Studio.DesignEffects

Rectangle {
    id: rectangle
    width: 500
    height: 800
    color: "#ede7ee"
    property alias inpUser: inpUser
    property alias label: label
    clip: true

    Image {
        id: logo
        x: 74
        y: 29
        width: 351
        height: 346
        source: "../../../../../../../Downloads/Electron_(software_framework)-Logo.wine.png"
        fillMode: Image.PreserveAspectFit
    }

    Button {
        id: login
        x: 271
        y: 540
        text: qsTr("entrar")
        highlighted: true
        flat: false
    }

    Button {
        id: register
        x: 137
        y: 540
        text: qsTr("registrarse")
        clip: false
        highlighted: true
        flat: true
    }

    Image {
        id: imgUser
        x: 143
        y: 381
        width: 37
        height: 38
        source: "../../../../../../../Downloads/usuario.png"
        fillMode: Image.PreserveAspectFit
    }

    Image {
        id: imgLock
        x: 143
        y: 447
        width: 37
        height: 38
        source: "../../../../../../../Downloads/cerrar.png"
        fillMode: Image.PreserveAspectFit
    }
    TextInput {
        id: inpPass
        x: 186
        y: 447
        width: 170
        height: 38
        color: "#707070"
        text: qsTr("contraseña")
        font.pixelSize: 12
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        selectionColor: "#805c84"
        echoMode: TextInput.Password
        font.bold: false
    }

    TextInput {
        id: inpUser
        x: 180
        y: 381
        width: 176
        height: 38
        color: "#707070"
        text: qsTr("usuario")
        font.pixelSize: 12
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        selectionColor: "#805c84"
        font.bold: false
    }

    Label {
        id: label
        x: 174
        y: 633
        width: 153
        height: 13
        text: qsTr("...")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    states: [
        State {
            name: "State1"
        }
    ]
}
