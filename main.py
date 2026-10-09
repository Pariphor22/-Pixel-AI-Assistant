import math

import threading
import tkinter as tk
import customtkinter as ctk


try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from assistant import PixelAssistant
except ImportError:
    class PixelAssistant:
        def __init__(self, gui):
            self.gui = gui

        def process_command(self, cmd):
            self.gui.add_user(cmd)
            self.gui.add_bot(f"Demo mode: assistant.py not loaded. Received '{cmd}'")

        def run(self):
            self.gui.set_status("Listening...")
            self.gui.listening()
            self.gui.add_user("Hey Pixel!")
            self.gui.add_bot("Hello!")
            self.gui.idle()



#  Colors
BG = "#F5F3FF"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E0E7FF"

TEXT_PRIMARY = "#334155"
TEXT_MUTED = "#64748B"

ACCENT_CYAN = "#0D9488"
ACCENT_VIOLET = "#8B5CF6"
ACCENT_PINK = "#EC4899"

PASTEL_PINK = "#F9A8D4"

MODE_LABEL = {
    "idle": "Waiting",
    "listening": "Listening",
    "thinking": "Thinking",
    "speaking": "Speaking",
}

#  Pillow Colors (RGB) 
PASTEL_VIOLET_RGB = (196, 181, 253)
PASTEL_BLUE_RGB   = (147, 197, 253)
PASTEL_SKY_RGB    = (186, 230, 253)
PASTEL_PINK_RGB   = (249, 168, 212)
PASTEL_MINT_RGB   = (167, 243, 208)
ACCENT_PINK_RGB   = (244, 114, 182)

SIRI_PALETTES = {
    "idle": [
        PASTEL_VIOLET_RGB,
        PASTEL_BLUE_RGB,
        PASTEL_PINK_RGB,
        PASTEL_MINT_RGB,
    ],
    "listening": [
        PASTEL_BLUE_RGB,
        PASTEL_SKY_RGB,
        PASTEL_MINT_RGB,
        PASTEL_VIOLET_RGB,
    ],
    "thinking": [
        PASTEL_VIOLET_RGB,
        PASTEL_PINK_RGB,
        PASTEL_BLUE_RGB,
        PASTEL_MINT_RGB,
    ],
    "speaking": [
        PASTEL_MINT_RGB,
        PASTEL_PINK_RGB,
        ACCENT_PINK_RGB,
        PASTEL_BLUE_RGB,
        PASTEL_VIOLET_RGB,
    ],
}

SIRI_MOTION = {
    "idle":      {"speed": 0.025, "intensity": 0.7, "brightness": 0.85},
    "listening": {"speed": 0.055, "intensity": 1.15, "brightness": 0.95},
    "thinking":  {"speed": 0.040, "intensity": 0.90, "brightness": 0.90},
    "speaking":  {"speed": 0.070, "intensity": 1.30, "brightness": 0.95},
}


class SiriOrb:
    RENDER_SIZE = 180
    DISPLAY_SIZE = 240

    def __init__(self, canvas, cx, cy):
        self.canvas = canvas
        self.cx, self.cy = cx, cy
        self.t = 0.0
        self.mode = "idle"
        self.image_id = None
        self.tk_img = None
        self._running = True
        self.tick()

    def stop(self):
        self._running = False

    def set_mode(self, mode):
        self.mode = mode

    def tick(self):
        if not self._running or not self.canvas.winfo_exists():
            return

        params = SIRI_MOTION[self.mode]
        colors = SIRI_PALETTES[self.mode]
        self.t += params["speed"]

        size = self.RENDER_SIZE
        c = size / 2
        base_r = size * 0.30

        img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        pulse = base_r + (base_r * 0.12) * math.sin(self.t * 1.7)

        for i, color in enumerate(colors):
            angle = self.t * (0.8 + i * 0.23) + i * (2 * math.pi / len(colors))
            orbit = pulse * 0.34 * params["intensity"]
            bx = c + orbit * math.cos(angle)
            by = c + orbit * math.sin(angle)
            br = pulse * (0.62 + 0.10 * math.sin(self.t * 2.3 + i))

            blob = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            d = ImageDraw.Draw(blob)
            alpha = int(210 * params["brightness"])
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=color + (alpha,))
            blob = blob.filter(ImageFilter.GaussianBlur(br * 0.35))
            img = Image.alpha_composite(img, blob)

        core = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        dc = ImageDraw.Draw(core)
        core_r = pulse * 0.34
        dc.ellipse([c - core_r, c - core_r, c + core_r, c + core_r],
                   fill=(255, 255, 255, int(180 * params["brightness"])))
        core = core.filter(ImageFilter.GaussianBlur(core_r * 0.5))
        img = Image.alpha_composite(img, core)

        img = img.resize((self.DISPLAY_SIZE, self.DISPLAY_SIZE), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)

        if self.image_id is None:
            self.image_id = self.canvas.create_image(self.cx, self.cy, image=self.tk_img)
        else:
            self.canvas.itemconfig(self.image_id, image=self.tk_img)

        self.canvas.after(35, self.tick)


class PixelGUI:

    def __init__(self):
        ctk.set_appearance_mode("light")
        
        self.root = ctk.CTk()
        self.root.title("Pixel — AI Assistant")
        self.root.geometry("700x820")
        self.root.configure(fg_color=BG)

        self.f_eyebrow = ctk.CTkFont(family="Helvetica", size=15, weight="bold")
        self.f_title = ctk.CTkFont(family="Helvetica", size=28, weight="bold")
        self.f_status = ctk.CTkFont(family="Helvetica", size=10, weight="bold")
        self.f_msg = ctk.CTkFont(family="Helvetica", size=15, weight="normal")
        self.f_btn = ctk.CTkFont(family="Helvetica", size=14, weight="bold")

        self.mode = "idle"
        self.assistant = PixelAssistant(self)
        self.listening_thread = None

        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


     
        

    def draw_gradient(self, canvas):
        

         width = 1500
         height = 160

         r1, g1, b1 = (236, 72, 153)
         r2, g2, b2 = (196, 181, 253)

         for i in range(height):

          r = int(r1 + (r2-r1) * i / height)
          g = int(g1 + (g2-g1) * i / height)
          b = int(b1 + (b2-b1) * i / height)

          color = f"#{r:02x}{g:02x}{b:02x}"

          canvas.create_line(
            0,
            i,
            width,
            i,
            fill=color
        )
        
     
        

    def _build_layout(self):
        # Header
        header = ctk.CTkFrame(self.root, fg_color=BG)
        header.pack(fill="x", padx=12, pady=(12, 4))

        left = ctk.CTkFrame(header, fg_color=BG)
        left.pack(side="left")

        ctk.CTkLabel(left, text="Desktop Assistant", font=self.f_eyebrow, fg_color=BG, text_color=ACCENT_VIOLET).pack(anchor="w")
        ctk.CTkLabel(left, text="Pixel AI ✨", font=self.f_title, fg_color=BG, text_color=TEXT_PRIMARY).pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            header, text="Waiting", font=self.f_status, fg_color=CARD_BG, text_color=TEXT_PRIMARY,
            corner_radius=12, border_width=1, border_color=CARD_BORDER, padx=12, pady=4
        )
        self.status_label.pack(side="right")

        # Orb Container Card
        orb_card = ctk.CTkFrame(
            self.root,
            corner_radius=24,
            fg_color=PASTEL_PINK,
            border_width=1,
            border_color=CARD_BORDER,
        )
        orb_card.pack(fill="x", padx=12, pady=8)

        # Standard Tkinter Canvas inside CTkFrame (Fixes ctk.CTkCanvas error)
        orb_canvas = tk.Canvas(
            orb_card,
            width=560,
            height=160,
            bg=PASTEL_PINK,
            highlightthickness=0,
            bd=0,
        )
        orb_canvas.pack(fill="both", expand=True)
        self.siri_orb = SiriOrb(
        orb_canvas,
        orb_canvas.winfo_reqwidth() // 2,
        orb_canvas.winfo_reqheight() // 2
     )

        def center_orb(event):
         self.siri_orb.cx = event.width // 2
         self.siri_orb.cy = event.height // 2

         if self.siri_orb.image_id:
            orb_canvas.coords(
            self.siri_orb.image_id,
            self.siri_orb.cx,
            self.siri_orb.cy
        )

        orb_canvas.bind("<Configure>", center_orb)
        self.draw_gradient(orb_canvas)
        orb_canvas.update_idletasks()

        center_x = orb_canvas.winfo_reqwidth() // 2
        center_y = orb_canvas.winfo_reqheight() // 2

        self.siri_orb = SiriOrb(
        orb_canvas,
        center_x,
        center_y
        )

        # Chat Text Box using CTkTextbox
        chat_frame = ctk.CTkFrame(self.root, fg_color=CARD_BG, corner_radius=16, border_width=1, border_color=CARD_BORDER)
        chat_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.chat = ctk.CTkTextbox(
            chat_frame, wrap="word", font=self.f_msg, fg_color=CARD_BG, text_color=TEXT_PRIMARY,
            corner_radius=16, border_width=0
        )
        self.chat.pack(fill="both", expand=True, padx=6, pady=6)

        # Safely configure tags on internal Tkinter Text widget
        raw_text = getattr(self.chat, "_textbox", None) or getattr(self.chat, "textbox", None)
        if raw_text:
            raw_text.tag_config("user_sender", foreground=ACCENT_CYAN, font=("Helvetica", 16, "bold"))
            raw_text.tag_config("bot_sender", foreground="#D946EF", font=("Helvetica", 16, "bold"))
            raw_text.tag_config("msg", foreground=TEXT_PRIMARY, font=("Helvetica", 18, "normal"))

        self.chat.configure(state="disabled")

        # Command Input Bar
        input_frame = ctk.CTkFrame(self.root, fg_color=BG)
        input_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.entry_var = tk.StringVar()
        self.cmd_entry = ctk.CTkEntry(
            input_frame, textvariable=self.entry_var, font=self.f_msg,
            fg_color=CARD_BG, text_color=TEXT_PRIMARY, border_color=CARD_BORDER,
            border_width=1, corner_radius=12, placeholder_text="Type a command..."
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))
        self.cmd_entry.bind("<Return>", lambda e: self.send_text_command())

        send_btn = ctk.CTkButton(
            input_frame, text="Send", font=self.f_btn, fg_color=ACCENT_VIOLET,
            hover_color="#7C3AED", text_color="#FFFFFF", corner_radius=12,
            command=self.send_text_command, width=80
        )
        send_btn.pack(side="right")

        # Bottom Buttons
        controls = ctk.CTkFrame(self.root, fg_color=BG)
        controls.pack(fill="x", padx=16, pady=(0, 16))

        mic_btn = ctk.CTkButton(
            controls, text="🎤 Start Listening", font=self.f_btn, fg_color=ACCENT_VIOLET,
            hover_color="#7C3AED", text_color="#FFFFFF", corner_radius=16,
            command=self.start_assistant
        )
        mic_btn.pack(side="left")

        clear_btn = ctk.CTkButton(
            controls, text="Clear", font=self.f_btn, fg_color=CARD_BG,
            hover_color="#F1F5F9", text_color=TEXT_MUTED, border_width=1,
            border_color=CARD_BORDER, corner_radius=12, command=self.clear_chat, width=80
        )
        clear_btn.pack(side="left", padx=8)

        exit_btn = ctk.CTkButton(
            controls, text="Exit", font=self.f_btn, fg_color=CARD_BG,
            hover_color="#FEE2E2", text_color=ACCENT_PINK, border_width=1,
            border_color=CARD_BORDER, corner_radius=12, command=self.on_close, width=80
        )
        exit_btn.pack(side="right")

    def send_text_command(self):
        text = self.entry_var.get().strip()
        if text:
            self.entry_var.set("")
            self.add_user(text)
            threading.Thread(target=self.assistant.process_command, args=(text,), daemon=True).start()

    def start_assistant(self):
        if not self.listening_thread or not self.listening_thread.is_alive():
            self.listening_thread = threading.Thread(target=self.assistant.run, daemon=True)
            self.listening_thread.start()

    def clear_chat(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")

    def _append(self, sender_label, sender_tag, text):
        self.chat.configure(state="normal")
        if self.chat.get("1.0", "end-1c") != "":
            self.chat.insert("end", "\n")
        
        raw_text = getattr(self.chat, "_textbox", None) or getattr(self.chat, "textbox", None)
        if raw_text:
            raw_text.insert("end", sender_label + "\n", sender_tag)
            raw_text.insert("end", text + "\n", "msg")
        else:
            self.chat.insert("end", f"{sender_label}\n{text}\n")
            
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def add_user(self, text):
        self._append("You", "user_sender", text)

    def add_bot(self, text):
        self._append("Pixel🤖", "bot_sender", text)

    def set_status(self, text):
        clean = text.replace("Status :", "").strip()
        self.status_label.configure(text=clean)

    def _set_mode(self, mode):
        self.mode = mode
        if hasattr(self, 'siri_orb') and self.siri_orb:
            self.siri_orb.set_mode(mode)
        self.status_label.configure(text=MODE_LABEL[mode])

    def listening(self): self._set_mode("listening")
    def speaking(self): self._set_mode("speaking")
    def thinking(self): self._set_mode("thinking")
    def idle(self): self._set_mode("idle")

    def on_close(self):
        if hasattr(self, 'siri_orb'):
            self.siri_orb.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PixelGUI()
    app.run()