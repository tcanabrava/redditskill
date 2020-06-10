import QtQuick 2.4
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.4
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: root

    property var images: sessionData.images

    Mycroft.SlideShow {
        id: imageSlideShow
        model: images
        anchors.fill: parent
        interval: 2000
        running: true
        loop: true

        delegate: Kirigami.AbstractCard {
            width: imageSlideShow.width
            height: imageSlideShow.height
            contentItem: ColumnLayout {
                anchors.fill: parent
                Kirigami.Heading {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    level: 3
                    text: model.Title
                }
                Kirigami.Separator {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                }
                Image {
                    Layout.fillWidth: true
                    Layout.preferredHeight: imageSlideShow.height
                    source: model.Image
                    fillMode: Image.PreserveAspectCrop
                }
            }
        }
    }
}