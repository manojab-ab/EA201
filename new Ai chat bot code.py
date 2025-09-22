import tkinter as tk
from tkinter import ttk
import heapq
import re
import difflib

# --- Campus Graph ---
graph = {
    "Flag Pole": {
        "walk": {"Hostel Block": 720, "Food Court": 350, "Sports Area": 1000, "Engineering Block": 200, "Academic Block": 40},
        "vehicle": {"Hostel Block": 720, "Food Court": 350, "Sports Area": 1000, "Engineering Block": 200, "Academic Block": 40}
    },
    "Hostel Block": {
        "walk": {"Flag Pole": 720, "Food Court": 150, "Sports Area": 200},
        "vehicle": {"Flag Pole": 720, "Food Court": 100, "Sports Area": 200}
    },
    "Food Court": {
        "walk": {"Flag Pole": 350, "Hostel Block": 150, "Engineering Block": 180},
        "vehicle": {"Flag Pole": 350, "Hostel Block": 100, "Engineering Block": 150}
    },
    "Sports Area": {
        "walk": {"Flag Pole": 1000, "Hostel Block": 200},
        "vehicle": {"Flag Pole": 1000, "Hostel Block": 200}
    },
    "Engineering Block": {
        "walk": {"Flag Pole": 200, "Food Court": 180, "Academic Block": 150},
        "vehicle": {"Flag Pole": 200, "Food Court": 150, "Academic Block": 150}
    },
    "Academic Block": {
        "walk": {"Flag Pole": 40, "Engineering Block": 150},
        "vehicle": {"Flag Pole": 40, "Engineering Block": 200}
    }
}

places = list(graph.keys())

# --- Timings ---
timings = {
    "Academic Block": "9:30 AM – 5:30 PM",
    "Library": "9:30 AM – 8:00 PM",
    "Hostel Block": "5:00 AM – 10:00 PM",
    "Entrance": "6:00 AM – 7:30 PM",
    "Sports Area": "10:00 AM – 7:30 PM",
    "Food Court": "8:00 AM – 10:00 PM",
    "Flag Pole": "Accessible at all times"
}

# --- FAQ ---
faq = {
    "Food Court": "The Food Court is near the Hostel Block and Flag Pole. Facilities: Breakfast, lunch, snacks, dinner, indoor games, gym.",
    "Sports Area": "The Sports Area is behind the Hostel Block. Facilities: Basketball, football, cricket, volleyball.",
    "Academic Block": "The Academic Block is beside the Flag Pole and close to the Engineering Block. Facilities: Classrooms, seminar halls, faculty offices, Auditorium.",
    "Engineering Block": "The Engineering Block is beside the Academic Block and close to the Food Court. Facilities: Labs, project rooms, lecture halls.",
    "Hostel Block": "The Hostel Block is opposite the Food Court. Facilities: Rooms, common area, mess hall.",
    "Flag Pole": "The Flag Pole is a central landmark near the Academic Block. Often used as a meeting point for events.",
    "Library": "The Library is inside the Academic Block. Facilities: Books, journals, reading rooms.",
    "Entrance": "The Entrance is the main gate of the campus."
}

# --- Synonyms for locations ---
synonyms = {
    "food court": ["canteen", "mess", "dining hall"],
    "hostel block": ["dorm", "residence", "hostel"],
    "academic block": ["academics", "classes", "study block"],
    "engineering block": ["engg block", "labs", "engineering"],
    "sports area": ["playground", "field", "stadium", "sports"],
    "flag pole": ["main pole", "flag", "landmark"],
    "library": ["books", "reading hall", "study area"],
    "entrance": ["main gate", "entry", "gate"]
}

def normalize_place(user_text):
    """Match user text to closest known place or synonym"""
    user_text = user_text.lower()
    for place, keys in synonyms.items():
        if place in user_text:
            return place.title()
        for k in keys:
            if k in user_text:
                return place.title()
    all_places = [p.lower() for p in places] + list(synonyms.keys())
    match = difflib.get_close_matches(user_text, all_places, n=1, cutoff=0.6)
    if match:
        return match[0].title()
    return None

# --- Shortest Path ---
def shortest_path(start, end, mode):
    pq = [(0, start, [])]
    visited = set()
    while pq:
        dist, current, path = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        path = path + [current]
        if current == end:
            return dist, path
        for neighbor, d in graph.get(current, {}).get(mode, {}).items():
            if neighbor not in visited:
                heapq.heappush(pq, (dist + d, neighbor, path))
    return float("inf"), []

# --- GUI ---
class CampusChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chanakya Campus Chatbot")
        self.root.geometry("700x650")

        self.chat_frame = tk.Text(root, state='disabled', wrap='word', bg="#f0f0f0")
        self.chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(self.button_frame, text="Select an option:", font=("Arial", 12, "bold")).pack(pady=5)

        tk.Button(self.button_frame, text="FAQs", width=20, command=self.show_faqs).pack(pady=2)
        tk.Button(self.button_frame, text="Check Timing", width=20, command=self.check_time).pack(pady=2)
        tk.Button(self.button_frame, text="Plan Travel", width=20, command=self.plan_travel).pack(pady=2)
        tk.Button(self.button_frame, text="Exit", width=20, command=root.quit).pack(pady=2)

        # --- Chat Input ---
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(padx=10, pady=10, fill=tk.X)

        self.entry = tk.Entry(self.entry_frame, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)

        self.bot_speak("Hi! I’m your Chanakya Campus Chatbot.\nUse the buttons or chat with me below.")

    def bot_speak(self, msg):
        self.chat_frame.configure(state='normal')
        self.chat_frame.insert(tk.END, "Bot: " + msg + "\n\n")
        self.chat_frame.configure(state='disabled')
        self.chat_frame.see(tk.END)

    def user_speak(self, msg):
        self.chat_frame.configure(state='normal')
        self.chat_frame.insert(tk.END, "You: " + msg + "\n")
        self.chat_frame.configure(state='disabled')
        self.chat_frame.see(tk.END)

    # --- Chat Handling ---
    def send_message(self, event=None):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return
        self.user_speak(user_msg)
        self.entry.delete(0, tk.END)
        self.process_message(user_msg.lower())

    def process_message(self, msg):
        # --- Greeting Queries ---
        if re.search(r"\b(hi|hii|hello|helo|hey|yo|good morning|good evening|namaste)\b", msg):
            self.bot_speak("Hi! I'm your Chanakya Campus Chatbot. You can ask about timings, locations, or travel.")
            return

        # --- Timing Queries ---
        for place in timings:
            if place.lower() in msg or normalize_place(msg) == place:
                if any(word in msg for word in ["time", "open", "close", "when"]):
                    self.bot_speak(f"{place} timings: {timings[place]}\nNote: Campus closed on Sunday.")
                    return

        # --- FAQ Queries ---
        for place in faq:
            if place.lower() in msg or normalize_place(msg) == place:
                self.bot_speak(f"{place}: {faq[place]}")
                return

        # --- Travel Queries ---
        travel_match = re.search(r"travel from (.+) to (.+) by (walk|vehicle)", msg)
        if travel_match:
            start = normalize_place(travel_match.group(1))
            end = normalize_place(travel_match.group(2))
            mode = travel_match.group(3).lower()
            if start in places and end in places:
                dist, path = shortest_path(start, end, mode)
                if path:
                    self.bot_speak(f"Best route ({mode}): {' -> '.join(path)} (Total {dist}m)")
                else:
                    self.bot_speak("Sorry, no route found.")
            else:
                self.bot_speak("I couldn't find those locations.")
            return

        # --- Default Fallback ---
        self.bot_speak("Sorry, I didn’t understand. You can ask about timings, locations, or travel.")

    # --- FAQ ---
    def show_faqs(self):
        faq_window = tk.Toplevel(self.root)
        faq_window.title("FAQs")
        tk.Label(faq_window, text="Select a FAQ:", font=("Arial", 12)).pack(pady=5)
        for place in faq:
            tk.Button(faq_window, text=place, width=30,
                      command=lambda p=place: self.display_faq(p, faq_window)).pack(pady=2)

    def display_faq(self, place, window):
        self.bot_speak(f"{place}: {faq[place]}")
        window.destroy()

    # --- Timing ---
    def check_time(self):
        time_window = tk.Toplevel(self.root)
        time_window.title("Check Timing")
        tk.Label(time_window, text="Select location:", font=("Arial", 12)).pack(pady=5)
        for place in timings:
            tk.Button(time_window, text=place, width=30,
                      command=lambda p=place: self.display_time(p, time_window)).pack(pady=2)

    def display_time(self, place, window):
        self.bot_speak(f"{place} timings: {timings[place]}\nNote: Campus will be closed on Sunday.")
        window.destroy()

    # --- Travel ---
    def plan_travel(self):
        travel_window = tk.Toplevel(self.root)
        travel_window.title("Plan Travel")
        tk.Label(travel_window, text="Select Start and End Locations", font=("Arial", 12)).pack(pady=5)

        start_var = tk.StringVar(value=places[0])
        end_var = tk.StringVar(value=places[0])

        tk.Label(travel_window, text="Start:").pack()
        start_cb = ttk.Combobox(travel_window, values=places, textvariable=start_var, state="readonly")
        start_cb.pack(pady=5)

        tk.Label(travel_window, text="End:").pack()
        end_cb = ttk.Combobox(travel_window, values=places, textvariable=end_var, state="readonly")
        end_cb.pack(pady=5)

        mode_var = tk.StringVar(value="walk")
        tk.Label(travel_window, text="Select Mode:").pack()
        tk.Radiobutton(travel_window, text="Walk", variable=mode_var, value="walk").pack()
        tk.Radiobutton(travel_window, text="Vehicle", variable=mode_var, value="vehicle").pack()

        def calculate_route():
            start = start_var.get()
            end = end_var.get()
            mode = mode_var.get()
            dist, path = shortest_path(start, end, mode)
            if path:
                self.bot_speak(f"Best route ({mode}): {' -> '.join(path)} (Total {dist}m)")
            else:
                self.bot_speak("Sorry, no route found.")
            travel_window.destroy()

        tk.Button(travel_window, text="Calculate Route", command=calculate_route).pack(pady=10)

# --- Run GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CampusChatbotGUI(root)
    root.mainloop()
