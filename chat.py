import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import speech_recognition as sr
import subprocess
import threading
import webbrowser

# === API Setup ===
API_KEY = "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"
recognizer = sr.Recognizer()

# === Global History ===
history = []
dark_mode = True

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            return recognizer.recognize_google(audio).lower()
        except:
            return ""

def chat_with_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are Salman GPT, a friendly assistant made by Sulman Ali Shah."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ Error: {e}"

# === GUI Setup ===
window = tk.Tk()
window.title("Salman GPT Assistant")
window.geometry("700x750")
window.configure(bg="#1e1e1e")

top_frame = tk.Frame(window, bg="#1e1e1e")
top_frame.pack(fill=tk.X)

icon_label = tk.Label(top_frame, text="🤖", font=("Segoe UI", 20), bg="#1e1e1e", fg="white")
icon_label.pack(side=tk.LEFT, padx=10, pady=10)

name_label = tk.Label(top_frame, text="Salman AI Assistant", font=("Segoe UI", 18, "bold"), bg="#1e1e1e", fg="white")
name_label.pack(side=tk.LEFT, pady=10)

chat_frame = tk.Frame(window, bg="#1e1e1e")
chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=("Consolas", 12),
                                         bg="#252526", fg="#dcdcdc", insertbackground="white",
                                         bd=0, relief=tk.FLAT)
chat_display.pack(expand=True, fill=tk.BOTH)
chat_display.config(state=tk.DISABLED)
chat_display.tag_config('user', foreground='cyan')
chat_display.tag_config('bot', foreground='lightgreen')

input_frame = tk.Frame(window, bg="#1e1e1e")
input_frame.pack(fill=tk.X, pady=10)

text_entry = tk.Entry(input_frame, font=("Segoe UI", 12), bg="#333", fg="white",
                      insertbackground="white", relief=tk.FLAT, highlightthickness=2, highlightcolor="#007acc")
text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), pady=5, ipady=8)
text_entry.focus()

def display_message(message, sender="user"):
    history.append((sender, message))
    chat_display.config(state=tk.NORMAL)
    if sender == "user":
        chat_display.insert(tk.END, f"\n🧑 You: {message}\n", 'user')
    else:
        chat_display.insert(tk.END, f"\n🤖 Salman GPT: {message}\n", 'bot')
    chat_display.config(state=tk.DISABLED)
    chat_display.yview(tk.END)

def handle_system_commands(command):
    if "open notepad" in command:
        subprocess.Popen(["notepad.exe"])
        return True
    elif "search" in command:
        query = command.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True
    return False

def start_text_chat():
    user_input = text_entry.get().strip()
    if not user_input:
        return
    display_message(user_input, "user")
    text_entry.delete(0, tk.END)
    if handle_system_commands(user_input):
        return
    threading.Thread(target=process_chat_response, args=(user_input,)).start()

def process_chat_response(prompt):
    response = chat_with_openrouter(prompt)
    display_message(response, "bot")

def start_voice_chat():
    while True:
        user_input = listen()
        if user_input in ['exit', 'quit', 'stop']:
            break
        if not user_input:
            continue
        display_message(user_input, "user")
        if handle_system_commands(user_input):
            continue
        response = chat_with_openrouter(user_input)
        display_message(response, "bot")

def style_button(btn):
    btn.config(bg="#007acc", fg="white", activebackground="#005a99",
               activeforeground="white", font=("Segoe UI", 11, "bold"),
               relief=tk.RAISED, bd=0, padx=10, pady=6, cursor="hand2")

send_button = tk.Button(input_frame, text="📤", command=start_text_chat)
style_button(send_button)
send_button.pack(side=tk.LEFT, padx=(5, 5), pady=5)

mic_button = tk.Button(input_frame, text="🎙️", command=lambda: threading.Thread(target=start_voice_chat).start())
style_button(mic_button)
mic_button.pack(side=tk.LEFT, padx=(5, 10), pady=5)

text_entry.bind("<Return>", lambda e: start_text_chat())

def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        window.configure(bg="#1e1e1e")
        top_frame.configure(bg="#1e1e1e")
        name_label.configure(bg="#1e1e1e", fg="white")
        icon_label.configure(bg="#1e1e1e", fg="white")
        chat_frame.configure(bg="#1e1e1e")
        chat_display.configure(bg="#252526", fg="#dcdcdc", insertbackground="white")
        input_frame.configure(bg="#1e1e1e")
        text_entry.configure(bg="#333", fg="white", insertbackground="white")
    else:
        window.configure(bg="white")
        top_frame.configure(bg="white")
        name_label.configure(bg="white", fg="black")
        icon_label.configure(bg="white", fg="black")
        chat_frame.configure(bg="white")
        chat_display.configure(bg="white", fg="black", insertbackground="black")
        input_frame.configure(bg="white")
        text_entry.configure(bg="#f0f0f0", fg="black", insertbackground="black")

toggle_button = tk.Button(window, text="🌓 Toggle Theme", command=toggle_mode)
style_button(toggle_button)
toggle_button.pack(pady=(0, 5))

def show_history():
    if not history:
        messagebox.showinfo("Chat History", "No history yet.")
        return
    history_text = "\n".join([f"{s.capitalize()}: {m}" for s, m in history])
    messagebox.showinfo("Chat History", history_text)

history_button = tk.Button(window, text="📜 View History", command=show_history)
style_button(history_button)
history_button.pack(pady=(0, 15))

window.mainloop()
