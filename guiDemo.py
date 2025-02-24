import tkinter as tk
from threading import Thread
from Database.chromadb_functions import load_database_from_dir
from Bots.simple_openai_bot import Simple_OpenAI_Bot
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database folder and loading
db_folder = "C:\\Users\\Stefan\\Workspace\\Code\\RAG_Bot\\Output"

def contains_sqlite3_file(folder_path):
    return any(file.endswith('.sqlite3') for file in os.listdir(folder_path))

if contains_sqlite3_file(db_folder):
    db = load_database_from_dir(db_folder)
    if not db:
        raise ValueError("Error loading the database!")
else:
    raise FileNotFoundError("No database was found at the specified location!")

# Bot setup
template = """You are an AI assistant for answering questions about a variety of topics. 
Be as helpful and resourceful as possible by using the context provided below.
Provide a conversational answer.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
If the question is not about the provided scientific material, politely decline to answer it.
=========
{context}
=========
Answer in Markdown:"""

my_bot = Simple_OpenAI_Bot(temperature=0, template=template, doc_retrieve_max=5)

class RAGBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAG Bot Chat")
        self.root.geometry("1280x720")
        self.root.configure(bg="#212121")

        # Frame for chat display
        self.chat_frame = tk.Frame(root, bg="#212121", padx=10, pady=10)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        # Chat display area
        self.chat_area = tk.Text(
            self.chat_frame, wrap=tk.WORD, state='disabled', width=80, height=25,
            font=("Arial", 12), bg="#303030", fg="#ffffff", highlightthickness=0, borderwidth=0
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # Frame for user input
        self.input_frame = tk.Frame(root, bg="#212121", padx=10, pady=10)
        self.input_frame.pack(fill=tk.X)

        # Left side: User input field
        self.input_field = tk.Entry(
            self.input_frame, font=("Arial", 14), width=50, bg="#5c5c5c", fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.input_field.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        # Right side: K value label + input + send button
        self.k_frame = tk.Frame(self.input_frame, bg="#212121")
        self.k_frame.pack(side=tk.RIGHT, padx=5)

        # Label "K: "
        self.k_label = tk.Label(
            self.k_frame, text="📄", font=("Arial", 12), bg="#212121", fg="#ffffff"
        )
        self.k_label.pack(side=tk.LEFT, padx=(0, 5))

        # Number validation function
        def validate_number_input(P):
            return P.isdigit() and int(P) >= 1 or P == ""

        vcmd = (root.register(validate_number_input), "%P")

        # Number field (to the right)
        self.number_field = tk.Entry(
            self.k_frame, font=("Arial", 12), width=5, bg="#5c5c5c", fg="#ffffff",
            validate="key", validatecommand=vcmd, insertbackground="#ffffff"
        )
        self.number_field.insert(0, "1")  # Default value
        self.number_field.pack(side=tk.LEFT, padx=(0, 5))

        # **Fix: Reset number to 1 only when focus is lost**
        self.number_field.bind("<FocusOut>", self.on_number_field_focus_out)

        # Send button (right below K field)
        self.send_button = tk.Button(
            self.k_frame, text="Send", font=("Arial", 12), bg="#0a6194", fg="#ffffff",
            command=self.ask_bot
        )
        self.send_button.pack(side=tk.LEFT)

        # Bind Enter key to send message
        self.input_field.bind("<Return>", lambda event: self.ask_bot())

    def on_number_field_focus_out(self, event):
        """Ensure number field always has a valid value when losing focus."""
        if self.number_field.get().strip() == "":
            self.number_field.insert(0, "1")  # Reset to 1 if empty

    def ask_bot(self):
        user_input = self.input_field.get().strip()
        user_k = self.number_field.get()
        if user_input:
            # Display user input immediately
            self.display_message(f"🧑: {user_input}", user=True)
            self.input_field.delete(0, tk.END)

            # Process bot response in a separate thread to not freeze window
            Thread(target=self.get_bot_response, args=(user_input,user_k)).start()

    def get_bot_response(self, user_input, user_k):
        retry = 0;
        try:
            bot_response = str(my_bot.ask(user_input, db,int(user_k))).replace("SOURCES: Unknown","").replace("SOURCES:","")
        except Exception as e:
            bot_response = f"Error: {str(e)}"

        if user_k!=1:
            user_k=1

        while bot_response == " I don't know.\n" and retry<6:
            retry=retry+1
            user_k=user_k+1
            try:
                bot_response = str(my_bot.ask(user_input, db,int(user_k))).replace("SOURCES: Unknown","").replace("SOURCES:","")
            except Exception as e:
                bot_response = f"Error: {str(e)}"

        self.display_message(f"🤖: {bot_response}", user=False)

    def display_message(self, message, user=False):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n\n", ("user" if user else "bot",))
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

        self.chat_area.tag_config("user", foreground="#8bc34a")
        self.chat_area.tag_config("bot", foreground="#ffffff")

if __name__ == "__main__":
    root = tk.Tk()
    app = RAGBotApp(root)
    root.mainloop()
