#!/usr/bin/env python3
"""
Social Media Uploader - Gabungan TikTok, Facebook (Status & Reels), dan YouTube Shorts
Dengan dukungan YouTube Data API v3
"""

import os
import sys
from pathlib import Path
from colorama import init, Fore, Style
import argparse

# Import uploader classes
from tiktok_uploader import TikTokUploader
from facebook_uploader import FacebookUploader
from youtube_api_uploader import YouTubeAPIUploader

# Initialize colorama
init(autoreset=True)

class SocialMediaUploader:
    def __init__(self, headless: bool = False, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.tiktok_uploader = TikTokUploader(headless=headless, debug=debug)
        self.facebook_uploader = FacebookUploader(headless=headless, debug=debug)
        self.youtube_uploader = YouTubeAPIUploader(debug=debug)

    def _log(self, message: str, level: str = "INFO"):
        """Simple logging"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED
        }
        
        color = colors.get(level, Fore.WHITE)
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def upload_to_tiktok(self, video_path: str, caption: str = "#fyp #viral #trending"):
        """Upload video ke TikTok"""
        self._log("Memulai upload ke TikTok...")
        return self.tiktok_uploader.upload_video(video_path, caption)

    def upload_to_facebook_status(self, status_text: str = "", media_path: str = ""):
        """Upload status ke Facebook dengan dukungan media"""
        self._log("Memulai upload status ke Facebook...")
        return self.facebook_uploader.upload_status(status_text, media_path)

    def upload_to_facebook_reels(self, video_path: str, description: str = ""):
        """Upload reels ke Facebook"""
        self._log("Memulai upload reels ke Facebook...")
        return self.facebook_uploader.upload_reels(video_path, description)

    def upload_to_youtube_shorts(self, video_path: str, title: str, description: str = "", privacy: str = "public"):
        """Upload shorts ke YouTube menggunakan API"""
        self._log("Memulai upload ke YouTube Shorts (API)...")
        
        # Initialize YouTube service
        if not self.youtube_uploader.initialize_youtube_service():
            return {
                "success": False,
                "message": "Gagal inisialisasi YouTube API"
            }
        
        return self.youtube_uploader.upload_shorts(video_path, title, description, privacy)

    def upload_to_all_video_platforms(self, video_path: str, tiktok_caption: str, facebook_description: str, youtube_title: str, youtube_description: str = "", youtube_privacy: str = "public"):
        """Upload video ke TikTok, Facebook Reels, dan YouTube Shorts sekaligus"""
        results = {}
        
        # Upload ke TikTok
        try:
            self._log("📱 Mengupload ke TikTok...", "INFO")
            tiktok_result = self.upload_to_tiktok(video_path, tiktok_caption)
            results['tiktok'] = tiktok_result
            
            if tiktok_result['success']:
                self._log("TikTok upload berhasil!", "SUCCESS")
            else:
                self._log(f"TikTok upload gagal: {tiktok_result['message']}", "ERROR")
        except Exception as e:
            self._log(f"Error TikTok upload: {str(e)}", "ERROR")
            results['tiktok'] = {"success": False, "message": str(e)}
        
        # Upload ke Facebook Reels
        try:
            self._log("📘 Mengupload reels ke Facebook...", "INFO")
            facebook_result = self.upload_to_facebook_reels(video_path, facebook_description)
            results['facebook_reels'] = facebook_result
            
            if facebook_result['success']:
                self._log("Facebook Reels upload berhasil!", "SUCCESS")
            else:
                self._log(f"Facebook Reels upload gagal: {facebook_result['message']}", "ERROR")
        except Exception as e:
            self._log(f"Error Facebook Reels upload: {str(e)}", "ERROR")
            results['facebook_reels'] = {"success": False, "message": str(e)}
        
        # Upload ke YouTube Shorts
        try:
            self._log("📺 Mengupload ke YouTube Shorts (API)...", "INFO")
            youtube_result = self.upload_to_youtube_shorts(video_path, youtube_title, youtube_description, youtube_privacy)
            results['youtube_shorts'] = youtube_result
            
            if youtube_result['success']:
                self._log("YouTube Shorts upload berhasil!", "SUCCESS")
                self._log(f"Video URL: {youtube_result.get('video_url', 'N/A')}", "INFO")
            else:
                self._log(f"YouTube Shorts upload gagal: {youtube_result['message']}", "ERROR")
        except Exception as e:
            self._log(f"Error YouTube Shorts upload: {str(e)}", "ERROR")
            results['youtube_shorts'] = {"success": False, "message": str(e)}
        
        return results

    def check_all_cookies(self):
        """Cek status cookies untuk semua platform"""
        self._log("📱 Status Cookies TikTok:", "INFO")
        self.tiktok_uploader.check_cookies_status()
        
        print()  # Empty line
        
        self._log("📘 Status Cookies Facebook:", "INFO")
        self.facebook_uploader.check_cookies_status()
        
        print()  # Empty line
        
        self._log("📺 Status Credentials YouTube API:", "INFO")
        self.youtube_uploader.check_credentials_status()

    def clear_all_cookies(self):
        """Hapus cookies untuk semua platform"""
        self._log("Menghapus cookies TikTok...", "INFO")
        self.tiktok_uploader.clear_cookies()
        
        self._log("Menghapus cookies Facebook...", "INFO")
        self.facebook_uploader.clear_cookies()
        
        self._log("Menghapus credentials YouTube...", "INFO")
        self.youtube_uploader.clear_credentials()
        
        self._log("Semua cookies/credentials berhasil dihapus!", "SUCCESS")

    def check_youtube_quota(self):
        """Cek YouTube API quota"""
        self._log("📺 Mengecek YouTube API Quota:", "INFO")
        return self.youtube_uploader.check_api_quota()

    def get_youtube_channel_info(self):
        """Get YouTube channel info"""
        self._log("📺 Mengambil info channel YouTube:", "INFO")
        if self.youtube_uploader.initialize_youtube_service():
            return self.youtube_uploader.get_channel_info()
        else:
            return {"success": False, "message": "Gagal inisialisasi YouTube API"}


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="Social Media Uploader (TikTok + Facebook + YouTube API)")
    parser.add_argument("--video", "-v", help="Path ke file video")
    parser.add_argument("--media", "-m", help="Path ke file media (video/gambar) untuk Facebook status")
    parser.add_argument("--tiktok-caption", "-tc", default="#fyp #viral #trending", help="Caption untuk TikTok")
    parser.add_argument("--facebook-status", "-fs", help="Status text untuk Facebook")
    parser.add_argument("--facebook-description", "-fd", default="", help="Deskripsi untuk Facebook Reels")
    parser.add_argument("--youtube-title", "-yt", help="Title untuk YouTube Shorts")
    parser.add_argument("--youtube-description", "-yd", default="", help="Deskripsi untuk YouTube Shorts")
    parser.add_argument("--youtube-privacy", "-yp", choices=['public', 'unlisted', 'private'], default='public', help="Privacy YouTube")
    parser.add_argument("--headless", action="store_true", help="Jalankan dalam mode headless")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-cookies", action="store_true", help="Hapus semua cookies")
    parser.add_argument("--check-cookies", action="store_true", help="Cek status semua cookies")
    parser.add_argument("--check-youtube-quota", action="store_true", help="Cek YouTube API quota")
    parser.add_argument("--youtube-channel-info", action="store_true", help="Info channel YouTube")
    parser.add_argument("--platform", "-p", choices=['tiktok', 'facebook-status', 'facebook-reels', 'youtube-shorts', 'all-video'], help="Platform target")
    
    args = parser.parse_args()
    
    uploader = SocialMediaUploader(headless=args.headless, debug=args.debug)
    
    # Handle different actions
    if args.clear_cookies:
        uploader.clear_all_cookies()
        return
    
    if args.check_cookies:
        uploader.check_all_cookies()
        return
    
    if args.check_youtube_quota:
        uploader.check_youtube_quota()
        return
    
    if args.youtube_channel_info:
        uploader.get_youtube_channel_info()
        return
    
    # Handle platform-specific uploads
    if args.platform:
        if args.platform == 'tiktok':
            if not args.video:
                print(f"{Fore.RED}❌ Video path diperlukan untuk TikTok upload")
                sys.exit(1)
            if not os.path.exists(args.video):
                print(f"{Fore.RED}❌ File video tidak ditemukan: {args.video}")
                sys.exit(1)
            
            result = uploader.upload_to_tiktok(args.video, args.tiktok_caption)
            if result["success"]:
                print(f"{Fore.GREEN}🎉 TikTok upload berhasil!")
            else:
                print(f"{Fore.RED}❌ TikTok upload gagal: {result['message']}")
                sys.exit(1)
        
        elif args.platform == 'facebook-status':
            if not args.facebook_status and not args.media:
                print(f"{Fore.RED}❌ Status text atau media diperlukan untuk Facebook status")
                sys.exit(1)
            
            if args.media and not os.path.exists(args.media):
                print(f"{Fore.RED}❌ File media tidak ditemukan: {args.media}")
                sys.exit(1)
            
            result = uploader.upload_to_facebook_status(args.facebook_status or "", args.media or "")
            if result["success"]:
                print(f"{Fore.GREEN}🎉 Facebook status berhasil!")
            else:
                print(f"{Fore.RED}❌ Facebook status gagal: {result['message']}")
                sys.exit(1)
        
        elif args.platform == 'facebook-reels':
            if not args.video:
                print(f"{Fore.RED}❌ Video path diperlukan untuk Facebook Reels")
                sys.exit(1)
            if not os.path.exists(args.video):
                print(f"{Fore.RED}❌ File video tidak ditemukan: {args.video}")
                sys.exit(1)
            
            result = uploader.upload_to_facebook_reels(args.video, args.facebook_description)
            if result["success"]:
                print(f"{Fore.GREEN}🎉 Facebook Reels berhasil!")
            else:
                print(f"{Fore.RED}❌ Facebook Reels gagal: {result['message']}")
                sys.exit(1)
        
        elif args.platform == 'youtube-shorts':
            if not args.video:
                print(f"{Fore.RED}❌ Video path diperlukan untuk YouTube Shorts")
                sys.exit(1)
            if not os.path.exists(args.video):
                print(f"{Fore.RED}❌ File video tidak ditemukan: {args.video}")
                sys.exit(1)
            if not args.youtube_title:
                print(f"{Fore.RED}❌ Title diperlukan untuk YouTube Shorts")
                sys.exit(1)
            
            result = uploader.upload_to_youtube_shorts(args.video, args.youtube_title, args.youtube_description, args.youtube_privacy)
            if result["success"]:
                print(f"{Fore.GREEN}🎉 YouTube Shorts berhasil!")
                print(f"{Fore.CYAN}📺 Video URL: {result.get('video_url', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ YouTube Shorts gagal: {result['message']}")
                sys.exit(1)
        
        elif args.platform == 'all-video':
            if not args.video:
                print(f"{Fore.RED}❌ Video path diperlukan untuk upload video ke semua platform")
                sys.exit(1)
            if not os.path.exists(args.video):
                print(f"{Fore.RED}❌ File video tidak ditemukan: {args.video}")
                sys.exit(1)
            if not args.youtube_title:
                print(f"{Fore.RED}❌ YouTube title diperlukan untuk upload ke semua platform")
                sys.exit(1)
            
            results = uploader.upload_to_all_video_platforms(
                args.video, 
                args.tiktok_caption, 
                args.facebook_description, 
                args.youtube_title, 
                args.youtube_description, 
                args.youtube_privacy
            )
            
            success_count = sum(1 for result in results.values() if result.get('success', False))
            total_count = len(results)
            
            if success_count == total_count:
                print(f"{Fore.GREEN}🎉 Semua upload video berhasil!")
            elif success_count > 0:
                print(f"{Fore.YELLOW}⚠️ {success_count}/{total_count} upload berhasil")
            else:
                print(f"{Fore.RED}❌ Semua upload gagal")
                sys.exit(1)
        
        return
    
    # Interactive mode
    print(f"{Fore.MAGENTA}🚀 Social Media Uploader")
    print("=" * 60)
    print(f"{Fore.YELLOW}🔥 TikTok + Facebook + YouTube API v3")
    print()
    
    while True:
        print(f"\n{Fore.YELLOW}Pilih platform:")
        print("1. 📱 TikTok (Upload Video)")
        print("2. 📝 Facebook Status (Text/Media)")
        print("3. 🎬 Facebook Reels (Upload Video)")
        print("4. 📺 YouTube Shorts (Upload Video - API)")
        print("5. 🚀 Upload Video ke SEMUA Platform")
        print("6. 🍪 Cek Status Cookies/Credentials")
        print("7. 📊 YouTube Channel Info")
        print("8. 🔍 Cek YouTube API Quota")
        print("9. 🗑️ Hapus Semua Cookies/Credentials")
        print("10. ❌ Keluar")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-10): ").strip()
        
        if choice == "1":
            video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
            if not os.path.exists(video_path):
                print(f"{Fore.RED}❌ File tidak ditemukan!")
                continue
            
            caption = input(f"{Fore.CYAN}Caption TikTok (Enter untuk default): ").strip()
            if not caption:
                caption = "#fyp #viral #trending"
            
            result = uploader.upload_to_tiktok(video_path, caption)
            
            if result["success"]:
                print(f"{Fore.GREEN}🎉 TikTok upload berhasil!")
            else:
                print(f"{Fore.RED}❌ TikTok upload gagal: {result['message']}")
        
        elif choice == "2":
            print(f"\n{Fore.YELLOW}📝 Facebook Status Options:")
            print("1. Text Only")
            print("2. Text + Media")
            print("3. Media Only")
            
            status_choice = input(f"{Fore.WHITE}Pilihan (1-3): ").strip()
            
            status_text = ""
            media_path = ""
            
            if status_choice in ["1", "2"]:
                status_text = input(f"{Fore.CYAN}Status Facebook: ").strip()
                if not status_text and status_choice == "1":
                    print(f"{Fore.RED}❌ Status text tidak boleh kosong untuk text only!")
                    continue
            
            if status_choice in ["2", "3"]:
                media_path = input(f"{Fore.CYAN}Path ke file media (video/gambar): ").strip()
                if not os.path.exists(media_path):
                    print(f"{Fore.RED}❌ File media tidak ditemukan!")
                    continue
            
            if not status_text and not media_path:
                print(f"{Fore.RED}❌ Minimal status text atau media diperlukan!")
                continue
            
            result = uploader.upload_to_facebook_status(status_text, media_path)
            
            if result["success"]:
                print(f"{Fore.GREEN}🎉 Facebook status berhasil!")
            else:
                print(f"{Fore.RED}❌ Facebook status gagal: {result['message']}")
        
        elif choice == "3":
            video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
            if not os.path.exists(video_path):
                print(f"{Fore.RED}❌ File tidak ditemukan!")
                continue
            
            description = input(f"{Fore.CYAN}Deskripsi Facebook Reels (opsional): ").strip()
            
            result = uploader.upload_to_facebook_reels(video_path, description)
            
            if result["success"]:
                print(f"{Fore.GREEN}🎉 Facebook Reels berhasil!")
            else:
                print(f"{Fore.RED}❌ Facebook Reels gagal: {result['message']}")
        
        elif choice == "4":
            video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
            if not os.path.exists(video_path):
                print(f"{Fore.RED}❌ File tidak ditemukan!")
                continue
            
            title = input(f"{Fore.CYAN}Title YouTube Shorts: ").strip()
            if not title:
                print(f"{Fore.RED}❌ Title tidak boleh kosong!")
                continue
            
            description = input(f"{Fore.CYAN}Deskripsi YouTube (opsional): ").strip()
            
            print(f"\n{Fore.YELLOW}Pilih privacy:")
            print("1. Public")
            print("2. Unlisted")
            print("3. Private")
            
            privacy_choice = input(f"{Fore.WHITE}Pilihan (1-3, default: 1): ").strip()
            privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
            privacy = privacy_map.get(privacy_choice, "public")
            
            result = uploader.upload_to_youtube_shorts(video_path, title, description, privacy)
            
            if result["success"]:
                print(f"{Fore.GREEN}🎉 YouTube Shorts berhasil!")
                print(f"{Fore.CYAN}📺 Video URL: {result.get('video_url', 'N/A')}")
                print(f"{Fore.CYAN}🆔 Video ID: {result.get('video_id', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ YouTube Shorts gagal: {result['message']}")
        
        elif choice == "5":
            video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
            if not os.path.exists(video_path):
                print(f"{Fore.RED}❌ File tidak ditemukan!")
                continue
            
            print(f"\n{Fore.YELLOW}📱 TikTok Settings:")
            tiktok_caption = input(f"{Fore.CYAN}Caption TikTok (Enter untuk default): ").strip()
            if not tiktok_caption:
                tiktok_caption = "#fyp #viral #trending"
            
            print(f"\n{Fore.YELLOW}📘 Facebook Settings:")
            facebook_description = input(f"{Fore.CYAN}Deskripsi Facebook Reels (opsional): ").strip()
            
            print(f"\n{Fore.YELLOW}📺 YouTube Settings:")
            youtube_title = input(f"{Fore.CYAN}Title YouTube Shorts: ").strip()
            if not youtube_title:
                print(f"{Fore.RED}❌ YouTube title tidak boleh kosong!")
                continue
            
            youtube_description = input(f"{Fore.CYAN}Deskripsi YouTube (opsional): ").strip()
            
            print(f"\n{Fore.YELLOW}Pilih privacy YouTube:")
            print("1. Public")
            print("2. Unlisted")
            print("3. Private")
            
            privacy_choice = input(f"{Fore.WHITE}Pilihan (1-3, default: 1): ").strip()
            privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
            youtube_privacy = privacy_map.get(privacy_choice, "public")
            
            print(f"\n{Fore.MAGENTA}🚀 Memulai upload ke SEMUA platform...")
            print(f"📱 TikTok: {tiktok_caption}")
            print(f"📘 Facebook: {facebook_description or 'Tanpa deskripsi'}")
            print(f"📺 YouTube: {youtube_title} ({youtube_privacy})")
            
            confirm = input(f"\n{Fore.YELLOW}Lanjutkan upload? (y/N): ").strip().lower()
            if confirm != 'y':
                continue
            
            results = uploader.upload_to_all_video_platforms(
                video_path, 
                tiktok_caption, 
                facebook_description, 
                youtube_title, 
                youtube_description, 
                youtube_privacy
            )
            
            success_count = sum(1 for result in results.values() if result.get('success', False))
            total_count = len(results)
            
            print(f"\n{Fore.MAGENTA}📊 HASIL UPLOAD:")
            for platform, result in results.items():
                status = "✅ BERHASIL" if result.get('success', False) else "❌ GAGAL"
                print(f"{platform.upper()}: {status}")
                if result.get('success') and 'video_url' in result:
                    print(f"   🔗 URL: {result['video_url']}")
            
            if success_count == total_count:
                print(f"\n{Fore.GREEN}🎉 SEMUA upload video berhasil! ({success_count}/{total_count})")
            elif success_count > 0:
                print(f"\n{Fore.YELLOW}⚠️ Sebagian berhasil: {success_count}/{total_count} upload berhasil")
            else:
                print(f"\n{Fore.RED}❌ Semua upload gagal")
        
        elif choice == "6":
            uploader.check_all_cookies()
        
        elif choice == "7":
            uploader.get_youtube_channel_info()
        
        elif choice == "8":
            uploader.check_youtube_quota()
        
        elif choice == "9":
            confirm = input(f"{Fore.YELLOW}Yakin ingin menghapus semua cookies/credentials? (y/N): ").strip().lower()
            if confirm == 'y':
                uploader.clear_all_cookies()
        
        elif choice == "10":
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