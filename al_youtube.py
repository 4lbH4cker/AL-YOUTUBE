import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
import queue
import time

class YouTubeDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AL-YOUTUBE Downloader - by 4lbH4cker")
        self.setup_ui()
        self.download_thread = None
        self.cancel_flag = False
        self.message_queue = queue.Queue()
        
        # Kontrollo mesazhet çdo 100ms
        self.root.after(100, self.process_messages)
    
    def setup_ui(self):
        self.root.geometry("600x450")
        
        # Header
        header_frame = tk.Frame(self.root)
        header_frame.pack(pady=10)
        tk.Label(header_frame, text="AL-YOUTUBE", font=("Arial", 24, "bold"), fg="red").pack()
        
        # URL Input
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(input_frame, text="by 4lbH4cker", fg="red", font=("Arial", 12)).pack(anchor=tk.W)
        tk.Label(input_frame, text="Github: https://github.com/4lbH4cker", fg="blue", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(input_frame, text="Shkruaj URL e YouTube (video ose playlist):", font=("Arial", 11)).pack(anchor=tk.W)
        self.url_entry = tk.Entry(input_frame, width=70, font=("Arial", 10))
        self.url_entry.pack(pady=5, fill=tk.X)
        
        # Progress Display
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(progress_frame, text="Progresi:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.progress_var = tk.StringVar(value="Duke pritur për shkarkim...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var, fg="blue", font=("Arial", 10), wraplength=550, justify=tk.LEFT)
        self.progress_label.pack(anchor=tk.W)
        
        tk.Label(progress_frame, text="Statusi:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        self.status_var = tk.StringVar(value="Gati")
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var, fg="green", font=("Arial", 10), wraplength=550, justify=tk.LEFT)
        self.status_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        self.download_btn = tk.Button(
            button_frame, 
            text="SHKARKO", 
            command=self.start_download_thread, 
            bg="#FF0000", 
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            activebackground="#CC0000"
        )
        self.download_btn.pack(side=tk.LEFT, padx=10)
        
        self.cancel_btn = tk.Button(
            button_frame, 
            text="NDALO", 
            command=self.cancel_download, 
            bg="#666666", 
            fg="white",
            font=("Arial", 12),
            width=15,
            state=tk.DISABLED,
            activebackground="#555555"
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def process_messages(self):
        """Përpunon mesazhet nga thread-i i shkarkimit"""
        try:
            while True:
                msg_type, message = self.message_queue.get_nowait()
                
                if msg_type == "progress":
                    self.progress_var.set(message)
                elif msg_type == "status":
                    self.status_var.set(message)
                    if "error" in message.lower():
                        self.status_label.config(fg="red")
                    elif "sukses" in message.lower():
                        self.status_label.config(fg="green")
                    else:
                        self.status_label.config(fg="blue")
                elif msg_type == "update_buttons":
                    if message == "disable_download":
                        self.download_btn.config(state=tk.DISABLED)
                        self.cancel_btn.config(state=tk.NORMAL)
                    else:
                        self.download_btn.config(state=tk.NORMAL)
                        self.cancel_btn.config(state=tk.DISABLED)
                
                self.root.update()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_messages)
    
    def start_download_thread(self):
        """Nis shkarkimin në një thread të veçantë"""
        if self.download_thread and self.download_thread.is_alive():
            return
        
        url = self.url_entry.get().strip()
        if not url:
            self.message_queue.put(("status", "Gabim: Ju lutem shkruani një URL"))
            return
        
        self.cancel_flag = False
        self.message_queue.put(("status", "Po filloj shkarkimin..."))
        self.message_queue.put(("progress", "Po përgatitet..."))
        self.message_queue.put(("update_buttons", "disable_download"))
        
        self.download_thread = threading.Thread(target=self.perform_download, args=(url,), daemon=True)
        self.download_thread.start()
    
    def cancel_download(self):
        """Ndalon shkarkimin aktual"""
        self.cancel_flag = True
        self.message_queue.put(("status", "Po ndaloj shkarkimin..."))
        self.message_queue.put(("update_buttons", "enable_download"))
    
    def perform_download(self, url):
        """Kryen shkarkimin aktual"""
        try:
            save_path = filedialog.askdirectory()
            if not save_path or self.cancel_flag:
                self.message_queue.put(("status", "Shkarkimi u anulua"))
                self.message_queue.put(("update_buttons", "enable_download"))
                return
            
            # Konfigurim i veçantë për playlistat
            if "list=" in url.lower():
                self.process_playlist(url, save_path)
            else:
                self.process_single_video(url, save_path)
            
            if not self.cancel_flag:
                self.message_queue.put(("status", "Shkarkimi u përfundua me sukses!"))
                self.message_queue.put(("progress", "Gati për shkarkim të ri"))
        
        except Exception as e:
            self.message_queue.put(("status", f"Gabim serioz: {str(e)}"))
            self.message_queue.put(("progress", "Shkarkimi dështoi"))
        finally:
            self.message_queue.put(("update_buttons", "enable_download"))
            self.cancel_flag = False
    
    def process_playlist(self, playlist_url, save_path):
        """Përpunon një playlistë"""
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'playlist_items': '1-1000',  # MAX
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Marrja e informacionit me timeout
                self.message_queue.put(("status", "Po marr informacionin e playlistës..."))
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info or 'entries' not in info:
                    self.message_queue.put(("status", "Gabim: Nuk u gjet playlistë"))
                    return
                
                entries = [e for e in info['entries'] if e is not None]
                total = len(entries)
                playlist_title = info.get('title', 'Playlistë pa emër')
                
                self.message_queue.put(("status", f"Playlistë: {playlist_title}"))
                self.message_queue.put(("progress", f"Gjetur {total} video"))
                
                # Shkarko çdo video
                downloaded = 0
                for i, entry in enumerate(entries):
                    if self.cancel_flag:
                        break
                    
                    video_url = entry.get('url') or f"https://youtube.com/watch?v={entry['id']}"
                    video_title = entry.get('title', f"Video {i+1}")
                    
                    self.message_queue.put(("progress", 
                        f"Video {i+1}/{total}: {self.trim_text(video_title, 60)}"))
                    self.message_queue.put(("status", "Po shkarkoj..."))
                    
                    try:
                        ydl.download([video_url])
                        downloaded += 1
                    except Exception as e:
                        self.message_queue.put(("status", 
                            f"Gabim në video {i+1}: {str(e)}"))
                        continue
                
                if not self.cancel_flag:
                    self.message_queue.put(("status", 
                        f"Përfunduar: {downloaded}/{total} video u shkarkuan"))
        
        except yt_dlp.utils.DownloadError as e:
            self.message_queue.put(("status", f"Gabim shkarkimi: {str(e)}"))
        except Exception as e:
            self.message_queue.put(("status", f"Gabim i papritur: {str(e)}"))
    
    def process_single_video(self, video_url, save_path):
        """Përpunon një video të vetme"""
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.message_queue.put(("status", "Po marr informacionin e videos..."))
                info = ydl.extract_info(video_url, download=False)
                
                video_title = info.get('title', 'Video pa titull')
                self.message_queue.put(("progress", f"Titulli: {video_title}"))
                self.message_queue.put(("status", "Po shkarkoj video..."))
                
                ydl.download([video_url])
                self.message_queue.put(("status", "Videoja u shkarkua me sukses!"))
        
        except Exception as e:
            self.message_queue.put(("status", f"Gabim në shkarkim: {str(e)}"))
    
    def progress_hook(self, d):
        """Ndryshon progresin në bazë të statusit"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '?')
            speed = d.get('_speed_str', '?')
            self.message_queue.put(("progress", f"Shkarkim: {percent} - Shpejtësi: {speed}"))
        elif d['status'] == 'finished':
            self.message_queue.put(("progress", "Përpunimi i përfunduar"))
    
    def trim_text(self, text, length):
        """Shkurton tekstin nëse është shumë i gjatë"""
        if len(text) > length:
            return text[:length-3] + "..."
        return text

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.root.mainloop()