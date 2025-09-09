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

# --- Timings for each location ---
timings = {
    "Academic Block": "9:30 AM – 5:30 PM",
    "Library": "9:30 AM – 8:00 PM",
    "Hostel Block": "5:00 AM – 10:00 PM",
    "Entrance": "6:00 AM – 7:30 PM",
    "Sports Area": "10:00 AM – 7:30 PM",
    "Food Court": "8:00 AM – 10:00 PM",
    "Flag Pole": "Accessible at all times"
}

# --- FAQ with description ---
faq = {
    "where is the food court": "The Food Court is near the Hostel Block and Flag Pole. Facilities: Breakfast, lunch, snacks, beverages.",
    "where is the sports area": "The Sports Area is behind the Hostel Block and near the Flag Pole. Facilities: Basketball, football, cricket nets, gym.",
    "where is the academic block": "The Academic Block is beside the Flag Pole and close to the Engineering Block. Facilities: Classrooms, seminar halls, faculty offices.",
    "where is the engineering block": "The Engineering Block is beside the Academic Block and close to the Food Court. Facilities: Labs, project rooms, lecture halls.",
    "where is the hostel block": "The Hostel Block is opposite the Food Court and close to the Sports Area. Facilities: Rooms, common area, mess hall.",
    "where is the flag pole": "The Flag Pole is a central landmark near the Academic Block. Often used as a meeting point for events.",
    "where is the library": "The Library is inside the Academic Block. Facilities: Books, journals, reading rooms.",
    "where is the entrance": "The Entrance is the main gate of the campus."
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

# --- Helper: Select Place ---
def select_place(msg):
    print(f"\n{msg}")
    for i, p in enumerate(places, 1):
        print(f"{i}. {p}")
    while True:
        choice = input("Enter choice (1-6 or name): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(places):
            return places[int(choice) - 1]
        elif choice.title() in places:
            return choice.title()
        else:
            print("Invalid choice, try again.")

# --- Chatbot ---
def chatbot():
    print("Hi! I’m your Chanakya Campus Chatbot.")
    print("You can ask FAQs, check timings, or plan a travel route between locations.")
    print("Type 'exit' to quit.\n")

    while True:
        user = input("You: ").lower().strip()
        if user == "exit":
            print("Bot: Goodbye! Have a nice day.")
            break

        # FAQ check
        answered = False
        for key in faq:
            if key in user:
                print("Bot:", faq[key])
                answered = True
                break
        if answered:
            continue

        # Ask user what they want to do: travel or check time
        print("\nBot: What do you want to do?")
        print("1. Travel between locations")
        print("2. Check opening/closing time of a place")
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            # Travel
            start = select_place("Choose your starting location:")
            end = select_place("Choose your destination:")
            print("\nMode of travel:")
            print("1. Walk")
            print("2. Vehicle")
            mode_choice = input("Enter choice (1/2): ").strip()
            mode = "walk" if mode_choice == "1" else "vehicle"
            dist, path = shortest_path(start, end, mode)
            if path:
                print(f"\nBot: Best route ({mode}): {' -> '.join(path)} (Total {dist}m)")
            else:
                print("Bot: Sorry, I couldn't find a route.")

        elif choice == "2":
            # Check timing
            location = select_place("Which location's timing do you want to know?")
            time_info = timings.get(location, "Timing info not available.")
            print(f"\nBot: {location} timings: {time_info}\nNote: Campus will be closed on Sunday.")
        else:
            print("Bot: Invalid choice. Please enter 1 or 2.")

# --- Run ---
if __name__ == "__main__":
    chatbot()
