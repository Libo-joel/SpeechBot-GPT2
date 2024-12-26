import speech_recognition as sr
from transformers import AutoTokenizer, AutoModelForCausalLM
import pyttsx3
import tkinter as tk
from tkinter import scrolledtext

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Load tokenizer and model
model_name = "gpt2"  # You can use other models if preferred
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech rate
engine.setProperty('volume', 0.9)  # Adjust volume

# Add padding token if not present
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': '<pad>'})
    model.resize_token_embeddings(len(tokenizer))

# Function to capture speech input
def capture_speech():
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Error with the speech recognition service: {e}"
        except Exception:
            return "Listening timed out. Please try again."

# Function to generate a response
def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(
        inputs["input_ids"], 
        max_length=50, 
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Function to convert text to speech
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()

# Tkinter Interface
class SpeechToSpeechBotApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Speech-to-Speech Bot")
        self.root.geometry("600x400")
        
        # Title label
        self.title_label = tk.Label(root, text="Speech-to-Speech Bot", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15, font=("Arial", 10))
        self.chat_display.pack(padx=10, pady=10)
        self.chat_display.config(state=tk.DISABLED)

        # Buttons
        self.speech_button = tk.Button(root, text="Speak", font=("Arial", 12), command=self.handle_speech_input)
        self.speech_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.exit_button = tk.Button(root, text="Exit", font=("Arial", 12), command=self.exit_app)
        self.exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def update_chat_display(self, text, sender="User"):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {text}\n")
        self.chat_display.yview(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def handle_speech_input(self):
        user_input = capture_speech()
        self.update_chat_display(user_input, sender="User")
        if user_input.lower() == "exit":
            self.exit_app()
        else:
            bot_response = generate_response(user_input)
            self.update_chat_display(bot_response, sender="Bot")
            text_to_speech(bot_response)

    def exit_app(self):
        self.root.destroy()

# Main function to run the GUI bot
def main():
    root = tk.Tk()
    app = SpeechToSpeechBotApp(root)
    root.mainloop()

if _name_ == "_main_":
    main()