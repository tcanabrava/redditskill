import QtQuick 2.4
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.4
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: root

    ColumnLayout {
        Kirigami.Heading {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            level: 3
            text: sessionData.videoTitle
        }
        Kirigami.Separator {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
        }
        Mycroft.VideoPlayer {
            id: examplePlayer
            source: sessionData.videoUrl
            nextAction: "reddit.video.next"
            previousAction: "reddit.video.prev"

            // Undocumented, should be "play", "stop" or "pause"
            status: "play"
            onSourceChanged: {
                console.log("Changing source to", source)
            }
        }
    }
}
