#!/usr/bin/env python3
"""
YouTube Shorts Uploader menggunakan YouTube Data API v3
Lebih reliable dan tidak memerlukan Selenium
"""

import os
import sys
import json
import time
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init(autoreset=True)

class YouTubeAPIUploader:
    def __init__(self, debug: bool = False):
        """
        Initialize YouTube API Uploader
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.youtube = None
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.credentials_dir = self.base_dir / "credentials"
        self.credentials_dir.mkdir(exist_ok=True)
        self.token_path = self.credentials_dir / "youtube_token.json"
        self.credentials_path = self.credentials_dir / "youtube_credentials.json"
        
        # YouTube API scopes
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        
        # API service name and version
        self.api_service_name = "youtube"
        self.api_version = "v3"

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging dengan warna"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA
        }
        
        if level == "DEBUG" and not self.debug:
            return
            
        color = colors.get(level, Fore.WHITE)
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def setup_credentials(self):
        """Setup OAuth2 credentials untuk YouTube API"""
        self._log("Menyiapkan kredensial YouTube API...")
        
        # Cek apakah file credentials.json ada
        if not self.credentials_path.exists():
            self._log("File credentials.json tidak ditemukan!", "ERROR")
            self._log("Silakan download credentials.json dari Google Cloud Console:", "INFO")
            self._log("1. Buka https://console.cloud.google.com/", "INFO")
            self._log("2. Buat project baru atau pilih project existing", "INFO")
            self._log("3. Enable YouTube Data API v3", "INFO")
            self._log("4. Buat OAuth 2.0 Client ID credentials", "INFO")
            self._log("5. Download sebagai JSON dan simpan sebagai 'credentials/youtube_credentials.json'", "INFO")
            raise FileNotFoundError("File credentials.json diperlukan")
        
        creds = None
        
        # Load existing token jika ada
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), self.scopes)
                self._log("Token existing dimuat", "SUCCESS")
            except Exception as e:
                self._log(f"Error loading token: {e}", "WARNING")
                creds = None
        
        # Jika tidak ada credentials yang valid, lakukan OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    self._log("Merefresh token yang expired...")
                    creds.refresh(Request())
                    self._log("Token berhasil direfresh", "SUCCESS")
                except Exception as e:
                    self._log(f"Error refresh token: {e}", "WARNING")
                    creds = None
            
            if not creds:
                self._log("Memulai OAuth flow...", "INFO")
                self._log("Browser akan terbuka untuk autentikasi Google", "WARNING")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.scopes)
                creds = flow.run_local_server(port=0)
                self._log("Autentikasi berhasil!", "SUCCESS")
            
            # Simpan credentials untuk next time
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            self._log("Token disimpan untuk penggunaan selanjutnya", "SUCCESS")
        
        return creds

    def initialize_youtube_service(self):
        """Initialize YouTube API service"""
        try:
            creds = self.setup_credentials()
            self.youtube = build(self.api_service_name, self.api_version, credentials=creds)
            self._log("YouTube API service berhasil diinisialisasi", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"Gagal inisialisasi YouTube API: {str(e)}", "ERROR")
            return False

    def get_video_category_id(self, category_name: str = "Entertainment") -> str:
        """Get video category ID berdasarkan nama kategori"""
        category_mapping = {
            "Film & Animation": "1",
            "Autos & Vehicles": "2", 
            "Music": "10",
            "Pets & Animals": "15",
            "Sports": "17",
            "Travel & Events": "19",
            "Gaming": "20",
            "People & Blogs": "22",
            "Comedy": "23",
            "Entertainment": "24",
            "News & Politics": "25",
            "Howto & Style": "26",
            "Education": "27",
            "Science & Technology": "28",
            "Nonprofits & Activism": "29"
        }
        
        return category_mapping.get(category_name, "24")  # Default to Entertainment

    def detect_if_shorts(self, video_path: str) -> bool:
        """Deteksi apakah video adalah Shorts berdasarkan durasi dan aspek rasio"""
        try:
            # Untuk sementara, kita anggap semua video adalah Shorts
            # Bisa ditambahkan logic untuk cek durasi dan aspek rasio menggunakan ffmpeg
            return True
        except Exception as e:
            self._log(f"Error detecting shorts: {e}", "DEBUG")
            return False

    def upload_video(self, video_path: str, title: str, description: str = "", 
                    tags: list = None, category: str = "Entertainment", 
                    privacy: str = "public") -> Dict[str, Any]:
        """
        Upload video ke YouTube
        
        Args:
            video_path: Path ke file video
            title: Title video
            description: Deskripsi video
            tags: List tags untuk video
            category: Kategori video
            privacy: Privacy setting (public, unlisted, private)
            
        Returns:
            Dict dengan status upload dan video info
        """
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File video tidak ditemukan: {video_path}")
        
        # Validasi file video
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        self._log(f"Mengupload: {os.path.basename(video_path)} ({file_size:.2f}MB)")
        
        # Deteksi MIME type
        mime_type, _ = mimetypes.guess_type(video_path)
        if not mime_type or not mime_type.startswith('video/'):
            self._log("File bukan video yang valid", "ERROR")
            raise ValueError("File harus berupa video")
        
        # Setup tags
        if tags is None:
            tags = []
        
        # Deteksi apakah Shorts
        is_shorts = self.detect_if_shorts(video_path)
        if is_shorts:
            if "#Shorts" not in tags and "#shorts" not in tags:
                tags.append("#Shorts")
            self._log("Video terdeteksi sebagai YouTube Shorts", "INFO")
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': self.get_video_category_id(category)
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Prepare media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,  # Upload in single chunk
            resumable=True,
            mimetype=mime_type
        )
        
        try:
            self._log("Memulai upload ke YouTube...", "INFO")
            
            # Execute upload request
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Upload dengan progress tracking
            response = None
            error = None
            retry = 0
            max_retries = 3
            
            while response is None:
                try:
                    self._log(f"Upload attempt {retry + 1}/{max_retries + 1}")
                    status, response = insert_request.next_chunk()
                    
                    if status:
                        progress = int(status.progress() * 100)
                        self._log(f"Upload progress: {progress}%", "INFO")
                
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        error = f"HTTP Error {e.resp.status}: {e.content}"
                        self._log(f"Retriable error: {error}", "WARNING")
                        retry += 1
                        if retry > max_retries:
                            raise Exception(f"Max retries exceeded: {error}")
                        time.sleep(2 ** retry)  # Exponential backoff
                    else:
                        raise Exception(f"HTTP Error {e.resp.status}: {e.content}")
                
                except Exception as e:
                    error = str(e)
                    self._log(f"Upload error: {error}", "ERROR")
                    retry += 1
                    if retry > max_retries:
                        raise Exception(f"Upload failed after {max_retries} retries: {error}")
                    time.sleep(2 ** retry)
            
            if response:
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                self._log("Upload berhasil!", "SUCCESS")
                self._log(f"Video ID: {video_id}", "INFO")
                self._log(f"Video URL: {video_url}", "INFO")
                
                return {
                    "success": True,
                    "message": "Upload berhasil",
                    "video_id": video_id,
                    "video_url": video_url,
                    "title": title,
                    "description": description,
                    "privacy": privacy,
                    "is_shorts": is_shorts,
                    "file_size_mb": file_size
                }
            else:
                raise Exception("Upload gagal: No response received")
                
        except HttpError as e:
            error_msg = f"YouTube API Error: {e.resp.status} - {e.content}"
            self._log(error_msg, "ERROR")
            
            # Parse specific errors
            if e.resp.status == 403:
                self._log("Kemungkinan quota API habis atau akses ditolak", "ERROR")
            elif e.resp.status == 400:
                self._log("Request tidak valid, cek parameter upload", "ERROR")
            
            return {
                "success": False,
                "message": error_msg,
                "video_path": video_path,
                "title": title
            }
            
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            self._log(error_msg, "ERROR")
            
            return {
                "success": False,
                "message": error_msg,
                "video_path": video_path,
                "title": title
            }

    def upload_shorts(self, video_path: str, title: str, description: str = "", 
                     privacy: str = "public") -> Dict[str, Any]:
        """
        Upload YouTube Shorts (wrapper untuk upload_video dengan optimasi Shorts)
        
        Args:
            video_path: Path ke file video
            title: Title video
            description: Deskripsi video
            privacy: Privacy setting
            
        Returns:
            Dict dengan status upload
        """
        
        # Tambahkan tags khusus Shorts
        shorts_tags = ["#Shorts", "#YouTubeShorts", "#Short"]
        
        # Tambahkan hashtag Shorts ke description jika belum ada
        if "#Shorts" not in description and "#shorts" not in description:
            description = f"{description}\n\n#Shorts" if description else "#Shorts"
        
        self._log("Mengupload sebagai YouTube Shorts...", "INFO")
        
        return self.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=shorts_tags,
            category="Entertainment",
            privacy=privacy
        )

    def get_channel_info(self) -> Dict[str, Any]:
        """Get informasi channel YouTube"""
        try:
            if not self.youtube:
                if not self.initialize_youtube_service():
                    return {"success": False, "message": "Gagal inisialisasi YouTube API"}
            
            request = self.youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                channel_info = {
                    "success": True,
                    "channel_id": channel['id'],
                    "channel_title": channel['snippet']['title'],
                    "subscriber_count": channel['statistics'].get('subscriberCount', 'Hidden'),
                    "video_count": channel['statistics'].get('videoCount', '0'),
                    "view_count": channel['statistics'].get('viewCount', '0')
                }
                
                self._log(f"Channel: {channel_info['channel_title']}", "SUCCESS")
                self._log(f"Subscribers: {channel_info['subscriber_count']}", "INFO")
                self._log(f"Videos: {channel_info['video_count']}", "INFO")
                
                return channel_info
            else:
                return {"success": False, "message": "Channel tidak ditemukan"}
                
        except Exception as e:
            error_msg = f"Error getting channel info: {str(e)}"
            self._log(error_msg, "ERROR")
            return {"success": False, "message": error_msg}

    def check_api_quota(self) -> Dict[str, Any]:
        """Check API quota usage (estimasi)"""
        try:
            # Lakukan request sederhana untuk test quota
            if not self.youtube:
                if not self.initialize_youtube_service():
                    return {"success": False, "message": "Gagal inisialisasi YouTube API"}
            
            # Test dengan request ringan
            request = self.youtube.channels().list(
                part="id",
                mine=True
            )
            response = request.execute()
            
            self._log("API quota tersedia", "SUCCESS")
            return {
                "success": True,
                "message": "API quota tersedia",
                "quota_available": True
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                error_msg = "API quota habis atau akses ditolak"
                self._log(error_msg, "ERROR")
                return {
                    "success": False,
                    "message": error_msg,
                    "quota_available": False
                }
            else:
                error_msg = f"API Error: {e.resp.status}"
                self._log(error_msg, "ERROR")
                return {
                    "success": False,
                    "message": error_msg,
                    "quota_available": False
                }
        except Exception as e:
            error_msg = f"Error checking quota: {str(e)}"
            self._log(error_msg, "ERROR")
            return {
                "success": False,
                "message": error_msg,
                "quota_available": False
            }

    def clear_credentials(self):
        """Hapus credentials dan token"""
        try:
            if self.token_path.exists():
                self.token_path.unlink()
                self._log("Token YouTube berhasil dihapus", "SUCCESS")
            else:
                self._log("Tidak ada token YouTube untuk dihapus", "WARNING")
        except Exception as e:
            self._log(f"Gagal menghapus token: {str(e)}", "ERROR")

    def check_credentials_status(self):
        """Cek status credentials"""
        if not self.credentials_path.exists():
            self._log("File credentials.json tidak ditemukan", "ERROR")
            self._log("Download dari Google Cloud Console dan simpan sebagai 'credentials/youtube_credentials.json'", "INFO")
            return {"credentials_exists": False, "token_exists": False}
        
        self._log("File credentials.json ditemukan", "SUCCESS")
        
        if not self.token_path.exists():
            self._log("Token belum ada, perlu autentikasi", "WARNING")
            return {"credentials_exists": True, "token_exists": False}
        
        try:
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.scopes)
            if creds.valid:
                self._log("Token valid dan siap digunakan", "SUCCESS")
                return {"credentials_exists": True, "token_exists": True, "token_valid": True}
            elif creds.expired and creds.refresh_token:
                self._log("Token expired tapi bisa direfresh", "WARNING")
                return {"credentials_exists": True, "token_exists": True, "token_valid": False, "can_refresh": True}
            else:
                self._log("Token tidak valid, perlu autentikasi ulang", "WARNING")
                return {"credentials_exists": True, "token_exists": True, "token_valid": False, "can_refresh": False}
        except Exception as e:
            self._log(f"Error membaca token: {str(e)}", "ERROR")
            return {"credentials_exists": True, "token_exists": True, "token_valid": False, "error": str(e)}


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="YouTube API Uploader")
    parser.add_argument("--video", "-v", help="Path ke file video")
    parser.add_argument("--title", "-t", help="Title untuk video")
    parser.add_argument("--description", "-d", default="", help="Deskripsi untuk video")
    parser.add_argument("--privacy", choices=['public', 'unlisted', 'private'], default='public', help="Privacy setting")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-credentials", action="store_true", help="Hapus credentials")
    parser.add_argument("--check-credentials", action="store_true", help="Cek status credentials")
    parser.add_argument("--check-quota", action="store_true", help="Cek API quota")
    parser.add_argument("--channel-info", action="store_true", help="Tampilkan info channel")
    
    args = parser.parse_args()
    
    uploader = YouTubeAPIUploader(debug=args.debug)
    
    # Handle different actions
    if args.clear_credentials:
        uploader.clear_credentials()
        return
    
    if args.check_credentials:
        uploader.check_credentials_status()
        return
    
    if args.check_quota:
        uploader.check_api_quota()
        return
    
    if args.channel_info:
        if uploader.initialize_youtube_service():
            uploader.get_channel_info()
        return
    
    if args.video and args.title:
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ File video tidak ditemukan: {args.video}")
            sys.exit(1)
        
        # Initialize YouTube service
        if not uploader.initialize_youtube_service():
            print(f"{Fore.RED}❌ Gagal inisialisasi YouTube API")
            sys.exit(1)
        
        result = uploader.upload_shorts(args.video, args.title, args.description, args.privacy)
        
        if result["success"]:
            print(f"{Fore.GREEN}🎉 YouTube Shorts berhasil diupload!")
            print(f"{Fore.CYAN}📺 Video URL: {result['video_url']}")
        else:
            print(f"{Fore.RED}❌ YouTube Shorts gagal: {result['message']}")
            sys.exit(1)
    
    else:
        # Interactive mode
        print(f"{Fore.RED}📺 YouTube API Uploader")
        print("=" * 40)
        print(f"{Fore.YELLOW}🔑 Menggunakan YouTube Data API v3")
        print(f"{Fore.YELLOW}🚀 Lebih reliable tanpa Selenium")
        print()
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. 🎬 Upload YouTube Shorts")
            print("2. 📊 Info Channel")
            print("3. 🔍 Cek API Quota")
            print("4. 🔑 Cek Status Credentials")
            print("5. 🗑️ Hapus Credentials")
            print("6. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-6): ").strip()
            
            if choice == "1":
                video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
                if not os.path.exists(video_path):
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
                    continue
                
                title = input(f"{Fore.CYAN}Title video: ").strip()
                if not title:
                    print(f"{Fore.RED}❌ Title tidak boleh kosong!")
                    continue
                
                description = input(f"{Fore.CYAN}Deskripsi (opsional): ").strip()
                
                print(f"\n{Fore.YELLOW}Pilih privacy:")
                print("1. Public")
                print("2. Unlisted")
                print("3. Private")
                
                privacy_choice = input(f"{Fore.WHITE}Pilihan (1-3, default: 1): ").strip()
                privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
                privacy = privacy_map.get(privacy_choice, "public")
                
                print(f"\n{Fore.MAGENTA}🚀 Memulai upload YouTube Shorts...")
                
                # Initialize service
                if not uploader.initialize_youtube_service():
                    print(f"{Fore.RED}❌ Gagal inisialisasi YouTube API")
                    continue
                
                result = uploader.upload_shorts(video_path, title, description, privacy)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 YouTube Shorts berhasil diupload!")
                    print(f"{Fore.CYAN}📺 Video URL: {result['video_url']}")
                    print(f"{Fore.CYAN}🆔 Video ID: {result['video_id']}")
                else:
                    print(f"{Fore.RED}❌ YouTube Shorts gagal: {result['message']}")
            
            elif choice == "2":
                if uploader.initialize_youtube_service():
                    uploader.get_channel_info()
            
            elif choice == "3":
                uploader.check_api_quota()
            
            elif choice == "4":
                uploader.check_credentials_status()
            
            elif choice == "5":
                confirm = input(f"{Fore.YELLOW}Yakin ingin menghapus credentials? (y/N): ").strip().lower()
                if confirm == 'y':
                    uploader.clear_credentials()
            
            elif choice == "6":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error fatal: {str(e)}")
        sys.exit(1)