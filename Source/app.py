from moviepy.audio.io.AudioFileClip import AudioFileClip
from tkinter import ttk, messagebox
import tkinter as tk
import threading
import pytube
import sys
import os

DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
TITLE = "YouTube Downloader.."
WIDTH = 800
HEIGHT = 200


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # Main settings
        self.geometry(self.calculate_center_of_the_screen(WIDTH, HEIGHT))
        self.resizable(False, False)

        # Title
        self.title(TITLE)

        # Grid settings
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)

        # Widgets
        label = tk.Label(self, text="YouTube Downloader", font=('Arial', 14, 'bold'))
        label.grid(row=1, column=0, columnspan=2, pady=15)

        self.url = tk.Entry(self, width=300, font=('Arial', 13))
        self.url.grid(row=2, column=0, padx=10)

        self.combo = ttk.Combobox(self, width=100, font=('Arial', 13), state='readonly', values=("Audio", "Video"))
        self.combo.grid(row=2, column=1, padx=10)
        self.combo.current(0)

        button = tk.Button(self, text="Download", font=('Arial', 13),
                           command=lambda: threading.Thread(target=self.submit).start(),
                           bg='#45b592', activebackground="#389c7c", bd=0, height=2, width=15)
        button.grid(row=3, column=0, columnspan=2, pady=25)

        self.list_current_widgets = self.winfo_children()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ============================== Functions ==========================
    def _on_close(self):
        if tk.messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            self.quit()
            self.destroy()

    def calculate_center_of_the_screen(self, w, h):
        x = int(self.winfo_screenwidth() / 2 - w / 2)
        y = int(self.winfo_screenheight() / 3 - h / 2)
        return f"{w}x{h}+{x}+{y}"

    def set_widget_state(self, state):
        for widget in self.list_current_widgets:
            widget['state'] = state
            if state == "normal" and 'combobox' in widget.widgetName:
                widget['state'] = 'readonly'

    def submit(self):
        url = self.url.get()
        if url.rfind("youtube.com") == -1 and url.rfind("youtu.be") == -1:
            tk.messagebox.showerror("Error", "Invalid URL")
            return
        self.set_widget_state("disabled")

        progressbar = ttk.Progressbar(self, mode="indeterminate", length=400)
        progressbar.grid(row=4, column=0, columnspan=3)
        progressbar.start()
        status = tk.Label(self, text="Connecting...", font=('Arial', 10))
        status.grid(row=5, column=0, columnspan=3, pady=5)

        try:
            file_type = self.combo.get()
            self.geometry(self.calculate_center_of_the_screen(WIDTH, HEIGHT + 50))

            if "playlist" in url:
                playlist = pytube.Playlist(url)
                i = 1
                for video in playlist.videos:
                    status.config(text=f"[{i}/{len(playlist.videos)}] {video.title}")
                    self.download(video, file_type)
                    i += 1
            else:
                video = pytube.YouTube(url)
                status.config(text=video.title)
                self.download(video, file_type)
        except:
            tk.messagebox.showerror("Error", "Internal error or video not exist")
        else:
            tk.messagebox.showinfo("Confirm", "Done")

        status.grid_remove()
        progressbar.stop()
        progressbar.grid_remove()
        self.set_widget_state("normal")
        self.geometry(self.calculate_center_of_the_screen(WIDTH, HEIGHT))

    @staticmethod
    def download(video, file_type):
        if file_type == "Audio":
            filename = video.streams.filter(only_audio=True).last().download(
                output_path=DESKTOP + "/YoutubeDownloads/songs")
            [name, _] = os.path.splitext(filename)
            clip = AudioFileClip(filename)
            clip.write_audiofile(name + ".mp3", bitrate="192K")
            os.remove(filename)
            clip.close()
        elif file_type == "Video":
            video.streams.get_highest_resolution().download(output_path=DESKTOP + "/YoutubeDownloads/videos")


if __name__ == '__main__':
    app = Application()
    app.mainloop()
