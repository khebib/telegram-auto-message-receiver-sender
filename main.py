import json
import os
import asyncio
import sys
import tkinter as tk
from tkinter import Tk, Frame, Label, Entry, Button, StringVar, ttk, messagebox, Scrollbar, Canvas, CENTER, Text
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from colorama import Fore, Style, init
init(autoreset=True)

# Default config file path
config_file = 'config.json'
client = None  # Global client variable
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Load configuration
def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

# Save configuration
def save_config(data):
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=4)

def ask_code():
    code = StringVar()

    def on_submit():
        code.set(code_entry.get())
        code_window.quit()  # Close the window

    code_window = Tk()
    code_window.title("Enter Verification Code")
    code_window.geometry("300x100")
    code_window.resizable(False,False)
    code_label = Label(code_window, text="Enter the code you received:", pady=10)
    code_label.pack()
    code_entry = Entry(code_window)
    code_entry.pack()
    submit_button = Button(code_window, text="Submit", command=on_submit)
    submit_button.pack(pady=10)

    # Keep the window open until code is set
    code_window.mainloop()
    entered_code = code.get()
    code_window.destroy()
    print(f"Code entered: {entered_code}")  # Debugging line
    return entered_code

async def request_code():
    config = load_config()
    print("Requesting code...")
    await client.send_code_request(config['phone_number'])
    code = ask_code()
    print(f"Code received: {code}")
    try:
        await client.sign_in(config['phone_number'], code)
        print("Code verification successful!")
        return True
    except errors.SessionPasswordNeededError:
        # If 2FA is enabled
        print("2FA enabled, requesting password...")
        password = ask_code()  # Here, you might want to ask for the 2FA password instead
        await client.sign_in(password=password)
        print("Password verification successful!")
        return True
    except Exception as e:
        print(f"Code verification failed: {e}")
        return e

# Start the bot
def start_bot():
    global client
    try:
        config = load_config()
        client = TelegramClient(
            StringSession(),
            config['api_id'],
            config['api_hash']
        )
        loop.run_until_complete(client.connect())

        if not loop.run_until_complete(client.is_user_authorized()):
            print("User not authorized, requesting code...")
            request_result = loop.run_until_complete(request_code())
            if request_result == True:
                messagebox.showinfo("Success", "Bot started successfully!")
                loop.run_until_complete(main())
            else:
                messagebox.showerror("Error", f"Failed to start bot: {request_result}")
                print(f"Failed to start bot: {request_result}")  # Debugging line
        else:
            messagebox.showinfo("Success", "Bot started successfully!")
            loop.run_until_complete(main())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start bot: {e}")
        print(f"Failed to start bot: {e}")  # Debugging line

# Stop the bot
def stop_bot():
    global client
    if client:
        loop.run_until_complete(client.disconnect())
        messagebox.showinfo("Success", "Bot stopped successfully!")

# Forward messages
async def forward_messages():
    config = load_config()
    download_path = config['download_path']
    os.makedirs(download_path, exist_ok=True)
    
    try:
        async for message in client.iter_messages(int(config['channel_id'])):
            if message.text and "Oran" in message.text:
                try:
                    modified_text = f"{message.text}"
                    
                    if message.photo:
                        photo = await message.download_media(file=download_path)
                        await client.send_file(int(config['target_group_id']), photo, caption=modified_text)
                    else:
                        await client.send_message(int(config['target_group_id']), modified_text)
                        
                    print(f"Message sent: {modified_text}")
                    
                except errors.ChatForwardsRestrictedError:
                    print("Error: Cannot forward messages due to chat restrictions.")
                except errors.MediaInvalidError:
                    print("Error: Invalid media format.")
    except Exception as e:
        print(f"Error fetching messages: {e}")

# Main bot function
async def main():
    config = load_config()
    await client.start()
    print("Bot is running...")
    await forward_messages()

# Custom print function to redirect stdout to Text widget
class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', message)
        self.text_widget.see('end')  # Auto-scroll to the end
        self.text_widget.config(state='disabled')

    def flush(self):
        pass  # Needed for compatibility with the print function

# Create the application window
root = Tk()
root.title("Receiver/Sender Made by Khebib")
root.geometry("500x300")
root.resizable(False, False)
root.configure(bg="#2c3e50")
# Uygulamanın bulunduğu dizini al
application_path = os.path.dirname(__file__)
print(application_path)

# İco dosyasının tam yolunu oluştur
icon_path = os.path.join(application_path, "img", "receiversender.ico")
print(icon_path)

# İco dosyasını yükle
root.iconbitmap(icon_path)# Tab control
tab_control = ttk.Notebook(root)

# Bot tab
bot_tab = Frame(tab_control, bg="#34495e")
tab_control.add(bot_tab, text='Bot')

# Config tab with scrollable frame
config_tab = Frame(tab_control, bg="#34495e")
tab_control.add(config_tab, text='Config')

# Scrollable canvas
canvas = Canvas(config_tab, bg="#34495e")
scrollbar = Scrollbar(config_tab, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#34495e")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Variables
config = load_config()
download_path = StringVar(value=config.get('download_path', ''))
channel_id = StringVar(value=config.get('channel_id', ''))
target_group_id = StringVar(value=config.get('target_group_id', ''))
api_id = StringVar(value=config.get('api_id', ''))
api_hash = StringVar(value=config.get('api_hash', ''))
phone_number = StringVar(value=config.get('phone_number', ''))

# Function to add placeholder
def add_placeholder(entry, variable, placeholder):
    if variable.get() == "":
        entry.insert(0, placeholder)
        entry.config(fg='grey')
    entry.bind("<FocusIn>", lambda args: clear_placeholder(entry, variable, placeholder))
    entry.bind("<FocusOut>", lambda args: restore_placeholder(entry, variable, placeholder))

def clear_placeholder(entry, variable, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, 'end')
        entry.config(fg='black')

def restore_placeholder(entry, variable, placeholder):
    if entry.get() == '':
        entry.insert(0, placeholder)
        entry.config(fg='grey')
    else:
        variable.set(entry.get())

# Config tab UI
def create_label_entry(parent, text, variable, placeholder=None):
    frame = Frame(parent, bg="#34495e")
    label = Label(frame, text=text, bg="#34495e", fg="#ecf0f1", width=20, anchor='e')
    entry = Entry(frame, textvariable=variable, width=40)
    if placeholder:
        add_placeholder(entry, variable, placeholder)
    label.pack(side="left", padx=10, pady=5)
    entry.pack(side="right", padx=10, pady=5)
    frame.pack(anchor=CENTER, pady=5)

create_label_entry(scrollable_frame, "Download Path:", download_path,  placeholder= "C:/Users/User/Desktop/TelegramMedia")
create_label_entry(scrollable_frame, "Receive Channel/Group ID:", channel_id, placeholder="ID of the channel/group to receive the message")
create_label_entry(scrollable_frame, "Target Group ID:", target_group_id , placeholder="ID of the channel/group to send the message")
create_label_entry(scrollable_frame, "API ID:", api_id, placeholder="Telegram application API ID")
create_label_entry(scrollable_frame, "API Hash:", api_hash , placeholder= "Telegram application API Hash")
create_label_entry(scrollable_frame, "Phone Number:", phone_number, placeholder= "+90XXXXXXXXXX")

def save_settings():
    # Placeholder values
    placeholders = {
        'download_path': "C:/Users/User/Desktop/TelegramMedia",
        'channel_id': "ID of the channel/group to receive the message",
        'target_group_id': "ID of the channel/group to send the message",
        'api_id': "Telegram application API ID",
        'api_hash': "Telegram application API Hash",
        'phone_number': "+90XXXXXXXXXX"
    }

    data = {
        'download_path': download_path.get(),
        'channel_id': channel_id.get(),
        'target_group_id': target_group_id.get(),
        'api_id': api_id.get(),
        'api_hash': api_hash.get(),
        'phone_number': phone_number.get()
    }

    # Kontrol ve temizleme işlemi
    for key, placeholder in placeholders.items():
        if data[key] == placeholder or data[key] == '':
            data[key] = ''

    save_config(data)
    messagebox.showinfo("Success", "Settings saved successfully.")

Button(scrollable_frame, text="Save Settings", command=save_settings, width=20, bg="#2980b9", fg="#ecf0f1").pack(pady=20)


# Bot tab UI
button_frame = Frame(bot_tab, bg="#34495e")
button_frame.pack(pady=20)

start_button = Button(button_frame, text="Start Bot", command=start_bot, width=20, bg="#27ae60", fg="#ecf0f1", font=('Helvetica', 12, 'bold'))
start_button.pack(side="left", padx=10)

stop_button = Button(button_frame, text="Stop Bot", command=stop_bot, width=20, bg="#c0392b", fg="#ecf0f1", font=('Helvetica', 12, 'bold'))
stop_button.pack(side="left", padx=10)

# Output text box for print statements
output_text = Text(bot_tab, height=10, bg="#000000", fg="#ffffff", wrap="word", state='normal')
output_text.pack(fill="both", expand=True, padx=10, pady=10)

# ASCII Art
ascii_art = """
        ██╗  ██╗██╗  ██╗███████╗██████╗ ██╗██████╗ 
        ██║ ██╔╝██║  ██║██╔════ ██╔══██╗██║██╔══██╗
        █████╔╝ ███████║███████║██████╔╝██║██████╔╝
        ██╔═██╗ ██╔══██║██╔══╝  ██╔══██╗██║██╔══██╗
        ██║  ██╗██║  ██║███████╗██████╔╝██║██████╔╝
        ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝╚═════╝ 
              
        ~ Telegram Message Receiver/Sender Bot ~

                ~ github.com/khebib ~\n\n
"""

# Insert the ASCII art into the Text widget with purple color
output_text.tag_configure("purple", foreground="#800080")
output_text.insert(tk.END, ascii_art, "purple")
output_text.config(state=tk.DISABLED)  # Make the Text widget read-only

# Redirect stdout to the Text widget
sys.stdout = StdoutRedirector(output_text)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tab_control.pack(expand=1, fill='both')

root.mainloop()
