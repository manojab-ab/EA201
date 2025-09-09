import tkinter as tk
from tkinter import ttk
import heapq

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
    "Food Court": "The Food Court is near the Hostel Block and Flag Pole. Facilities: Breakfast, lunch, snacks, beverages.",
    "Sports Area": "The Sports Area is behind the Hostel Block and near the Flag Pole. Facilities: Basketball, football, cricket nets, gym.",
    "Academic Block": "The Academic Block is beside the Flag Pole and close to the Engineering Block. Facilities: Classrooms, seminar halls, faculty offices.",
    "Engineering Block": "The Engineering Block is beside the Academic Block and close to the Food Court. Facilities: Labs, project rooms, lecture halls.",
    "Hostel Block": "The Hostel Block is opposite the Food Court and close to the Sports Area. Facilities: Rooms, common area, mess hall.",
    "Flag Pole": "The Flag Pole is a central landmark near the Academic Block. Often used as a meeting point for events.",
    "Library": "The Library is inside the Academic Block. Facilities: Books, journals, reading rooms.",
    "Entrance": "The Entrance is the main gate of the campus."
}

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
        for neighbor, d in graph[current][mode].items():
            if neighbor not in visited:
                heapq.heappush(pq, (dist + d, neighbor, path))
    return float("inf"), []

# --- GUI ---
class CampusChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chanakya Campus Chatbot")
        self.root.geometry("700x600")

        self.chat_frame = tk.Text(root, state='disabled', wrap='word', bg="#f0f0f0")
        self.chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(self.button_frame, text="Select an option:", font=("Arial", 12, "bold")).pack(pady=5)

        tk.Button(self.button_frame, text="FAQs", width=20, command=self.show_faqs).pack(pady=5)
        tk.Button(self.button_frame, text="Check Timing", width=20, command=self.check_time).pack(pady=5)
        tk.Button(self.button_frame, text="Plan Travel", width=20, command=self.plan_travel).pack(pady=5)
        tk.Button(self.button_frame, text="Exit", width=20, command=root.quit).pack(pady=5)

        self.bot_speak("Hi! I’m your Chanakya Campus Chatbot.\nUse the buttons below to select an option.")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = CampusChatbotGUI(root)
    root.mainloop()

