import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from pyrogram import Client
from dotenv import load_dotenv
import aiohttp
import asyncio
from urllib.parse import urlparse, parse_qs
import time
from database import Database
from google_drive import GoogleDriveUploader
from config import ADMIN_IDS, PACKAGES

# Load environment variables
load_dotenv()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# Initialize Database
db = Database()

class FileUploadBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.gdrive_uploader = GoogleDriveUploader()
        
        # Initialize Pyrogram client for file uploads
        self.pyrogram_client = Client(
            "bot_session",
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.bot_token
        )
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Add user to database if not exists
        if not db.get_user(user_id):
            db.add_user(user_id, user_name)
        
        welcome_message = f"""
🎉 স্বাগতম {user_name}!

এই বট Direct Download Link থেকে ফাইল Telegram এবং Google Drive এ আপলোড করতে পারে।

📌 কমান্ড সমূহ:
/start - বট শুরু করুন
/help - সাহায্য দেখুন
/status - আপনার লিমিট দেখুন
/login - Google Drive লগইন করুন
/logout - Google Drive লগআউট করুন

📥 ব্যবহার পদ্ধতি:
শুধু একটি Direct Download Link পাঠান এবং বট স্বয়ংক্রিয়ভাবে ফাইল আপলোড করবে।

• ২GB এর কম: Telegram ও Google Drive উভয়ে আপলোড করা যাবে
• ২GB এর বেশি: শুধুমাত্র Google Drive এ আপলোড হবে
"""
        
        if user_id in ADMIN_IDS:
            welcome_message += "\n👑 আপনি একজন Admin। /admin কমান্ড ব্যবহার করুন।"
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
📖 সাহায্য

🔹 কিভাবে ব্যবহার করবেন:
১. একটি Direct Download Link পাঠান
২. ফাইল সাইজ অনুযায়ী আপলোড অপশন দেখুন
৩. আপনার পছন্দের অপশন সিলেক্ট করুন

🔹 ফাইল সাইজ লিমিট:
• ২GB এর কম: Telegram + Google Drive
• ২GB এর বেশি: শুধু Google Drive

🔹 মাসিক লিমিট:
আপনার প্যাকেজ অনুযায়ী মাসিক আপলোড লিমিট আছে। /status দিয়ে দেখুন।

🔹 Google Drive:
Google Drive এ আপলোড করতে /login দিয়ে লগইন করুন।
"""
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user status and limits"""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ ইউজার পাওয়া যায়নি। /start দিয়ে শুরু করুন।")
            return
        
        package_name = user['package']
        package_limit = PACKAGES[package_name]
        used_limit = user['monthly_used']
        remaining = package_limit - used_limit
        
        status_text = f"""
📊 আপনার স্ট্যাটাস

👤 ইউজার: {user['name']}
📦 প্যাকেজ: {package_name}
📈 মাসিক লিমিট: {self.format_size(package_limit)}
📊 ব্যবহৃত: {self.format_size(used_limit)}
✅ বাকি: {self.format_size(remaining)}

🔄 রিসেট হবে: প্রতি মাসের ১ তারিখে

🔗 Google Drive: {'✅ সংযুক্ত' if user['gdrive_token'] else '❌ সংযুক্ত নয়'}
"""
        await update.message.reply_text(status_text)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin panel"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই।")
            return
        
        keyboard = [
            [InlineKeyboardButton("👥 সব ইউজার দেখুন", callback_data="admin_users")],
            [InlineKeyboardButton("📦 প্যাকেজ পরিবর্তন করুন", callback_data="admin_package")],
            [InlineKeyboardButton("🔄 লিমিট রিসেট করুন", callback_data="admin_reset")],
            [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="admin_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👑 Admin Panel\n\nনিচের অপশন থেকে সিলেক্ট করুন:",
            reply_markup=reply_markup
        )
    
    async def handle_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct download links and OAuth callback URLs"""
        user_id = update.effective_user.id
        url = update.message.text.strip()
        
        # Check if this is an OAuth callback URL
        if 'localhost:8080' in url and 'code=' in url:
            await self.handle_oauth_callback(update, context, url)
            return
        
        # Validate URL
        if not self.is_valid_url(url):
            await update.message.reply_text("❌ অবৈধ লিংক। একটি সঠিক Direct Download Link দিন।")
            return
        
        # Check user exists
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ ইউজার পাওয়া যায়নি। /start দিয়ে শুরু করুন।")
            return
        
        # Get file info
        status_msg = await update.message.reply_text("🔍 ফাইল ইনফরমেশন চেক করা হচ্ছে...")
        
        try:
            file_info = await self.get_file_info(url)
            file_size = file_info['size']
            file_name = file_info['name']
            
            # Check monthly limit
            package_limit = PACKAGES[user['package']]
            if user['monthly_used'] + file_size > package_limit:
                remaining = package_limit - user['monthly_used']
                await status_msg.edit_text(
                    f"❌ মাসিক লিমিট শেষ!\n\n"
                    f"📊 বাকি: {self.format_size(remaining)}\n"
                    f"📁 ফাইল সাইজ: {self.format_size(file_size)}\n\n"
                    f"প্রয়োজন: {self.format_size(file_size - remaining)} বেশি"
                )
                return
            
            # Show file info and options
            size_gb = file_size / (1024**3)
            
            file_info_text = f"""
📁 ফাইল ইনফরমেশন

📝 নাম: {file_name}
📊 সাইজ: {self.format_size(file_size)}

📥 আপলোড অপশন নিচে থেকে সিলেক্ট করুন:
"""
            
            keyboard = []
            
            if size_gb < 2:
                # Under 2GB - Show both options
                keyboard.append([InlineKeyboardButton("📤 Telegram এ আপলোড করুন", callback_data=f"upload_tg_{user_id}")])
                keyboard.append([InlineKeyboardButton("☁️ Google Drive এ আপলোড করুন", callback_data=f"upload_gd_{user_id}")])
            else:
                # Over 2GB - Only Google Drive
                keyboard.append([InlineKeyboardButton("☁️ Google Drive এ আপলোড করুন", callback_data=f"upload_gd_{user_id}")])
                file_info_text += "\n⚠️ ফাইল ২GB এর বেশি, শুধুমাত্র Google Drive এ আপলোড করা যাবে।"
            
            keyboard.append([InlineKeyboardButton("❌ বাতিল করুন", callback_data="cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store URL in context
            context.user_data['pending_url'] = url
            context.user_data['file_info'] = file_info
            
            await status_msg.edit_text(file_info_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            await status_msg.edit_text(f"❌ ফাইল ইনফরমেশন পেতে সমস্যা হয়েছে:\n{str(e)}")
    
    async def handle_oauth_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_url: str):
        """Handle Google OAuth callback URL"""
        user_id = update.effective_user.id
        
        # Check if user was awaiting auth
        if not context.user_data.get('awaiting_gdrive_auth'):
            await update.message.reply_text(
                "❌ OAuth callback expected নয়।\n\n"
                "প্রথমে /login কমান্ড ব্যবহার করুন।"
            )
            return
        
        status_msg = await update.message.reply_text("🔄 Google Drive সংযুক্ত করা হচ্ছে...")
        
        try:
            # Extract authorization code from URL
            parsed_url = urlparse(callback_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' not in query_params:
                await status_msg.edit_text("❌ Authorization code পাওয়া যায়নি। আবার চেষ্টা করুন।")
                return
            
            auth_code = query_params['code'][0]
            
            # Exchange code for credentials
            token_dict = self.gdrive_uploader.get_credentials_from_code(auth_code)
            
            # Save token to database
            db.update_gdrive_token(user_id, token_dict)
            
            # Clear awaiting flag
            context.user_data['awaiting_gdrive_auth'] = False
            
            await status_msg.edit_text(
                "✅ সফলভাবে Google Drive সংযুক্ত হয়েছে!\n\n"
                "এখন আপনি Google Drive এ ফাইল আপলোড করতে পারবেন।"
            )
            
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            await status_msg.edit_text(
                f"❌ Google Drive সংযুক্ত করতে সমস্যা হয়েছে:\n{str(e)}\n\n"
                "আবার /login কমান্ড দিয়ে চেষ্টা করুন।"
            )
            context.user_data['awaiting_gdrive_auth'] = False
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        if data == "cancel":
            await query.edit_message_text("❌ বাতিল করা হয়েছে।")
            return
        
        # Admin callbacks
        if data.startswith("admin_"):
            if user_id not in ADMIN_IDS:
                await query.edit_message_text("❌ আপনার এই অপশন ব্যবহারের অনুমতি নেই।")
                return
            
            await self.handle_admin_callback(query, context)
            return
        
        # Upload callbacks
        if data.startswith("upload_"):
            await self.handle_upload_callback(query, context)
            return
    
    async def handle_upload_callback(self, query, context):
        """Handle upload button callbacks"""
        user_id = query.from_user.id
        data = query.data
        
        url = context.user_data.get('pending_url')
        file_info = context.user_data.get('file_info')
        
        if not url or not file_info:
            await query.edit_message_text("❌ ফাইল ইনফরমেশন পাওয়া যায়নি। আবার চেষ্টা করুন।")
            return
        
        if data.startswith("upload_tg_"):
            await self.upload_to_telegram(query, url, file_info, user_id)
        elif data.startswith("upload_gd_"):
            await self.upload_to_gdrive(query, url, file_info, user_id)
    
    async def upload_to_telegram(self, query, url, file_info, user_id):
        """Upload file to Telegram using Pyrogram - OPTIMIZED"""
        await query.edit_message_text("📥 Telegram এ আপলোড শুরু হচ্ছে...")
        
        try:
            # Download file
            progress_msg = await query.message.reply_text("⏳ ডাউনলোড হচ্ছে... 0%")
            
            download_start = time.time()
            file_path = await self.download_file(url, file_info['name'], progress_msg)
            download_time = time.time() - download_start
            
            download_speed = file_info['size'] / download_time if download_time > 0 else 0
            logger.info(f"Download completed: {self.format_size(download_speed)}/s")
            
            # Upload to Telegram using Pyrogram
            await progress_msg.edit_text("⏳ Telegram এ আপলোড হচ্ছে...")
            
            # Start Pyrogram client if not connected
            if not self.pyrogram_client.is_connected:
                await self.pyrogram_client.start()
                logger.info("Pyrogram client connected for upload")
            
            # Upload with progress callback
            last_progress = [0]
            last_time = [time.time()]
            
            async def progress_callback(current, total):
                percent = (current / total) * 100
                current_time = time.time()
                time_elapsed = current_time - last_time[0]
                
                # Update every 10% or every 2 seconds
                if (int(percent) - last_progress[0] >= 10) or (time_elapsed >= 2):
                    last_progress[0] = int(percent)
                    last_time[0] = current_time
                    
                    # Calculate upload speed
                    speed = current / (current_time - download_start - download_time) if (current_time - download_start - download_time) > 0 else 0
                    
                    try:
                        await progress_msg.edit_text(
                            f"⏳ Telegram এ আপলোড হচ্ছে... {int(percent)}%\n"
                            f"📊 {self.format_size(current)} / {self.format_size(total)}\n"
                            f"⚡ Speed: {self.format_size(speed)}/s"
                        )
                    except Exception as e:
                        logger.debug(f"Progress update error: {e}")
            
            # Send document with optimized settings
            upload_start = time.time()
            await self.pyrogram_client.send_document(
                chat_id=user_id,
                document=file_path,
                caption=f"📁 {file_info['name']}\n📊 Size: {self.format_size(file_info['size'])}",
                progress=progress_callback,
                file_name=file_info['name']
            )
            
            upload_time = time.time() - upload_start
            upload_speed = file_info['size'] / upload_time if upload_time > 0 else 0
            
            logger.info(f"Upload completed: {self.format_size(upload_speed)}/s")
            
            # Update user usage
            db.update_monthly_usage(user_id, file_info['size'])
            db.add_upload_record(user_id, file_info['name'], file_info['size'], 'telegram')
            
            await progress_msg.edit_text(
                f"✅ সফলভাবে Telegram এ আপলোড হয়েছে!\n\n"
                f"📥 Download Speed: {self.format_size(download_speed)}/s\n"
                f"📤 Upload Speed: {self.format_size(upload_speed)}/s"
            )
            
            # Delete temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
        except Exception as e:
            logger.error(f"Telegram upload error: {e}")
            await query.message.reply_text(f"❌ আপলোড ব্যর্থ হয়েছে:\n{str(e)}")
        finally:
            pass
    
    async def upload_to_gdrive(self, query, url, file_info, user_id):
        """Upload file to Google Drive"""
        user = db.get_user(user_id)
        
        if not user['gdrive_token']:
            keyboard = [[InlineKeyboardButton("🔗 Login করুন", callback_data="gdrive_login")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Google Drive সংযুক্ত নয়।\n\nপ্রথমে /login দিয়ে লগইন করুন।",
                reply_markup=reply_markup
            )
            return
        
        await query.edit_message_text("☁️ Google Drive এ আপলোড শুরু হচ্ছে...")
        
        try:
            progress_msg = await query.message.reply_text("⏳ ডাউনলোড হচ্ছে... 0%")
            
            # Download file
            file_path = await self.download_file(url, file_info['name'], progress_msg)
            
            # Upload to Google Drive
            await progress_msg.edit_text("⏳ Google Drive এ আপলোড হচ্ছে...")
            
            result = await self.gdrive_uploader.upload_file(
                file_path,
                file_info['name'],
                user['gdrive_token']
            )
            
            # Update user usage
            db.update_monthly_usage(user_id, file_info['size'])
            db.add_upload_record(user_id, file_info['name'], file_info['size'], 'gdrive')
            
            await progress_msg.edit_text(
                f"✅ সফলভাবে Google Drive এ আপলোড হয়েছে!\n\n"
                f"🔗 লিংক: {result['webViewLink']}"
            )
            
            # Delete temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
        except Exception as e:
            logger.error(f"Google Drive upload error: {e}")
            await query.message.reply_text(f"❌ আপলোড ব্যর্থ হয়েছে:\n{str(e)}")
    
    async def handle_admin_callback(self, query, context):
        """Handle admin panel callbacks"""
        data = query.data
        
        if data == "admin_users":
            users = db.get_all_users()
            text = "👥 সব ইউজার:\n\n"
            for user in users[:20]:
                text += f"• {user['name']} (ID: {user['user_id']})\n"
                text += f"  📦 {user['package']} | 📊 {self.format_size(user['monthly_used'])}\n\n"
            if len(users) > 20:
                text += f"\n... এবং আরো {len(users) - 20} জন ইউজার"
            await query.edit_message_text(text)
        
        elif data == "admin_stats":
            stats = db.get_statistics()
            text = f"""
📊 পরিসংখ্যান

👥 মোট ইউজার: {stats['total_users']}
📤 মোট আপলোড: {stats['total_uploads']}
💾 মোট ডাটা: {self.format_size(stats['total_data'])}
"""
            await query.edit_message_text(text)
        
        elif data == "admin_reset":
            keyboard = [
                [InlineKeyboardButton("✅ হ্যাঁ, সব রিসেট করুন", callback_data="admin_reset_confirm")],
                [InlineKeyboardButton("❌ না, বাতিল করুন", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "⚠️ সব ইউজারের মাসিক লিমিট রিসেট করতে চান?\n\nএটি সব ইউজারের monthly_used 0 করে দেবে।",
                reply_markup=reply_markup
            )
        
        elif data == "admin_reset_confirm":
            db.reset_monthly_usage()
            await query.edit_message_text("✅ সব ইউজারের মাসিক লিমিট রিসেট হয়ে গেছে!")
    
    async def get_file_info(self, url):
        """Get file information from URL"""
        import ssl
        
        # Create SSL context that doesn't verify certificates (for Termux compatibility)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    size = int(response.headers.get('Content-Length', 0))
                    
                    if size == 0:
                        # Try GET request for first few bytes
                        async with session.get(url, headers={'Range': 'bytes=0-1'}) as get_response:
                            content_range = get_response.headers.get('Content-Range', '')
                            if content_range:
                                size = int(content_range.split('/')[-1])
                    
                    # Get filename from URL or Content-Disposition
                    filename = None
                    if 'Content-Disposition' in response.headers:
                        content_disp = response.headers['Content-Disposition']
                        if 'filename=' in content_disp:
                            filename = content_disp.split('filename=')[1].strip('"')
                    
                    if not filename:
                        filename = os.path.basename(urlparse(url).path) or 'downloaded_file'
                    
                    return {
                        'name': filename,
                        'size': size
                    }
            except ssl.SSLError as e:
                logger.error(f"SSL Error: {e}")
                raise Exception("SSL সমস্যা। Termux packages update করুন: pkg update && pkg upgrade")
            except Exception as e:
                logger.error(f"Error getting file info: {e}")
                raise
    
    async def download_file(self, url, filename, progress_msg):
        """Download file from URL with progress - OPTIMIZED for high speed"""
        import ssl
        
        download_path = f"downloads/{filename}"
        os.makedirs("downloads", exist_ok=True)
        
        # Create SSL context for Termux compatibility
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Optimized connector settings for high-speed downloads
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            force_close=False,
            enable_cleanup_closed=True
        )
        
        last_time = time.time()
        
        # Use larger timeout for high-speed connections
        timeout = aiohttp.ClientTimeout(
            total=None,
            connect=30,
            sock_read=60
        )
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(url) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                # Use 10MB chunks for faster download (instead of 1MB)
                chunk_size = 10 * 1024 * 1024
                
                with open(download_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 3 seconds
                        current_time = time.time()
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            time_elapsed = current_time - last_time
                            
                            # Calculate download speed
                            if time_elapsed >= 3:
                                speed = downloaded / time_elapsed if time_elapsed > 0 else 0
                                try:
                                    await progress_msg.edit_text(
                                        f"⏳ ডাউনলোড হচ্ছে... {int(progress)}%\n"
                                        f"📊 {self.format_size(downloaded)} / {self.format_size(total_size)}\n"
                                        f"⚡ Speed: {self.format_size(speed)}/s"
                                    )
                                    last_time = current_time
                                except Exception as e:
                                    logger.debug(f"Progress update error: {e}")
        
        return download_path
    
    def is_valid_url(self, url):
        """Validate URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def format_size(self, size_bytes):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Google Drive login command"""
        user_id = update.effective_user.id
        
        # Check if user already has token
        user = db.get_user(user_id)
        if user and user['gdrive_token']:
            await update.message.reply_text(
                "✅ আপনি ইতিমধ্যে Google Drive এ লগইন করা আছেন!\n\n"
                "লগআউট করতে /logout ব্যবহার করুন।"
            )
            return
        
        auth_url = self.gdrive_uploader.get_auth_url(user_id)
        
        keyboard = [[InlineKeyboardButton("🔗 Google এ লগইন করুন", url=auth_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "☁️ Google Drive এক্সেস দিতে নিচের পদক্ষেপ অনুসরণ করুন:\n\n"
            "১. নিচের বাটন ক্লিক করুন\n"
            "২. Google account select করুন\n"
            "৩. 'Continue' ক্লিক করুন (যদি unsafe warning দেখেন)\n"
            "৪. 'Allow' করুন\n"
            "৫. Redirect হওয়ার পর URL টি সম্পূর্ণ কপি করুন\n"
            "৬. এই bot এ URL টি পাঠান\n\n"
            "📝 URL দেখতে এরকম হবে:\n"
            "http://localhost:8080/?state=...&code=...",
            reply_markup=reply_markup
        )
        
        # Mark user as waiting for auth code
        context.user_data['awaiting_gdrive_auth'] = True
    
    async def logout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Google Drive logout command"""
        user_id = update.effective_user.id
        db.update_gdrive_token(user_id, None)
        await update.message.reply_text("✅ Google Drive থেকে লগআউট হয়েছে।")
    
    async def initialize_pyrogram(self):
        """Initialize Pyrogram client"""
        if not self.pyrogram_client.is_connected:
            await self.pyrogram_client.start()
            logger.info("Pyrogram client initialized!")
    
    def run(self):
        """Run the bot"""
        # Create custom request with longer timeout
        request = HTTPXRequest(
            connection_pool_size=8,
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0
        )
        
        application = Application.builder()\
            .token(self.bot_token)\
            .request(request)\
            .build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CommandHandler("login", self.login_command))
        application.add_handler(CommandHandler("logout", self.logout_command))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_link))
        
        # Callback handlers
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start bot
        logger.info("Bot started!")
        
        try:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            # Cleanup Pyrogram client on shutdown
            if self.pyrogram_client.is_connected:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.pyrogram_client.stop())
                logger.info("Pyrogram client stopped!")

if __name__ == '__main__':
    bot = FileUploadBot()
    bot.run()