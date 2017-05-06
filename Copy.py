#Red_Devil

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os,sys,re,shutil

class PlaylistCopy(QDialog):

    def __init__(self):
        QDialog.__init__(self)

        layout = QGridLayout()
        sub_layout1 = QVBoxLayout()
        sub_layout2 = QVBoxLayout()

        self.playlist_location = QLineEdit()
        self.dest_location = QLineEdit()
        self.progress = QProgressBar()

        label = QLabel("Copy playlist songs to a directory")
        playlist_browse = QPushButton("Browse playlist")
        dest_browse = QPushButton("Choose destination directory")
        copy = QPushButton("Copy Files")
        self.progress.setValue(0)
        self.progress.setAlignment(Qt.AlignHCenter)
        self.playlist_location.setPlaceholderText("Select the playlist file")
        self.dest_location.setPlaceholderText("Choose the destination directory")

        sub_layout1.addWidget(label)
        sub_layout2.addWidget(copy)

        label.setAlignment(Qt.AlignHCenter)
        font = QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(15)
        label.setFont(font)
        font.setPointSize(9)
        playlist_browse.setFont(font)
        dest_browse.setFont(font)
#        playlist_browse.setFixedSize(100,25)
        self.playlist_location.setFixedSize(300,20)
        copy.setFixedSize(200,20)

#        layout.addLayout(sub_layout1,0,0,1,2)
        layout.addLayout(sub_layout2,3,0,1,2,Qt.AlignHCenter)
        layout.addWidget(label,0,0,1,2)
        layout.addWidget(self.playlist_location,1,0)
        layout.addWidget(playlist_browse,1,1)
        layout.addWidget(self.dest_location,2,0)
        layout.addWidget(dest_browse,2,1)
#        layout.addWidget(self.progress)
#        layout.addWidget(copy,3,0,1,2)

        playlist_browse.clicked.connect(self.playlist_browse)
        dest_browse.clicked.connect(self.dest_browse)
        copy.clicked.connect(self.copy)

        self.setLayout(layout)
        self.setWindowTitle("PlaylistCopy")
        self.setFocus()

    def playlist_browse(self):
        dest = QFileDialog.getOpenFileName(self,caption="Save File as",directory=".",filter="All Files(*.*)")
        if not(dest.endswith('.wpl')):
            QMessageBox.warning(self,"Warning","Choose a valid playlsit (.wpl file)")
        else:
            self.playlist_location.setText(QDir.toNativeSeparators(dest))

    def dest_browse(self):
        dest = QFileDialog.getExistingDirectory(self,caption="Save File as",directory=".")
        if not(os.path.exists(dest)):
            QMessageBox.warning(self,"Warning","The destination folder does not exsits")
        else:
            self.dest_location.setText(QDir.toNativeSeparators(dest))

    def copy(self):

        error = False
        path = self.playlist_location.text()

        if not(os.path.exists(path)):
            error = True
            QMessageBox.warning(self,"Warning","Choose playlist")

        dest = self.dest_location.text()

        if not(os.path.exists(dest)):
            error = True
            QMessageBox.warning(self,"Warning","Choose destination folder")

        path.replace("/","\\")
        if not(error):
            try:
                file = open(path)
                read = file.read()
                file = open(path)
                readLines = file.readlines()

                start = read.find('<title>')
                end = read.find('</title>')
                if start > 0 and end > 0:
                    folder_name = read[start+7:end]
                else:
                    folder_name = os.path.basename(path)
                total_songs = 0
                count = 0
                songs_list = []
                total_size = 0
                file_size = 0

                new_folder = os.path.join(dest,folder_name)
                print(new_folder)
                if os.path.exists(new_folder):
                    QMessageBox.warning(self,"Warning","A folder of name %s already exits in the destination" %folder_name)
                else:
                    os.mkdir(new_folder)

                    #Calculate total no of songs and make a list consisting of valid song paths
                    for song in readLines:
                        try:
                            song_name = re.search('<media src="(.+?)"',song).group(1)
                            if song_name[0:2] == '..':
                                song_name = song_name[2:]
                                os.chdir(os.path.dirname(path))
                                os.chdir('..')
                                song_path = os.getcwd()+song_name
                            else:
                                song_path = song_name
                            if(os.path.exists(song_path)):
                                songs_list.append(song_path)
                                total_songs = total_songs + 1
                                total_size = total_size + os.path.getsize(song_path)
                        except:
                            pass

                    total_size = total_size / 1024 / 1024
        #            print(total_songs)
        #            print(total_size)

                    if total_songs == 0:
                        QMessageBox.warning(self,"Warning","The playlist contains songs which have been modified.")
                    else:
                        progressDialog = QProgressDialog ("Copying Files...", "Abort", 0, 100)
                        progressDialog.setWindowTitle("PlaylistCopy")
                        bar = QProgressBar(progressDialog)
                        bar.setRange(0, 100)
                        bar.setValue(0)
                        progressDialog.setBar(bar)
                        progressDialog.setMinimumWidth(350)
                        progressDialog.setMinimumDuration(1000)
                        progressDialog.setWindowModality(Qt.WindowModal)
                        progressDialog.setValue(0)

                        for song_path in songs_list:
                            try:
                                name = os.path.basename(song_path)
                                count = count+1
                                new_path = os.path.join(new_folder,name)
                                print(song_path+' '+new_path)
                                if os.path.exists(new_path):
                                    QMessageBox.warning(self,"Warning","A file of name %s already exits in the destination" %name)
                                else:
                                    shutil.copy(song_path,new_path)
                                    percent = count * 100 / total_songs
                                    progressDialog.setValue(percent)
                                    bar.setValue(percent)
                                    self.progress.setValue(int(percent))
                                    file_size = file_size+os.path.getsize(song_path)
                                if progressDialog.wasCanceled():
                                    break
                            except:
                                pass

                        progressDialog.close()
                        QMessageBox.information(self,"Information","%d songs copied successfully." %count)

            except:
                pass

    def event(self, event):
        if event.type() == QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            QMessageBox.about(self,"About","This application copies all the songs from a playlist to destination directory."
                                               "<p> Simply choose the playlist and the destination folder. </p>"
                                                "The songs will be copied to a new folder (Playlist Name) in the destination folder ")
            return True
        return QDialog.event(self, event)

app = QApplication(sys.argv)
dialog = PlaylistCopy()
dialog.show()
app.exec_()
