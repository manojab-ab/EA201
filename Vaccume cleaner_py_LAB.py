import math

def calculate_distance(shape, params):
    if shape == "Square":
        side = params["side"]
        return 4 * side
    elif shape == "Circle":
        radius = params["radius"]
        return 2 * math.pi * radius
    elif shape == "Triangle":
        a = params["a"]
        b = params["b"]
        c = params["c"]
        return a + b + c
    elif shape == "Heptagon":
        side = params["side"]
        return 7 * side
    else:
        return 0

def get_params(shape):
    params = {}
    if shape == "Square":
        params["side"] = float(input("Enter side length of square: "))
    elif shape == "Circle":
        params["radius"] = float(input("Enter radius of circle: "))
    elif shape == "Triangle":
        params["a"] = float(input("Enter length of side a: "))
        params["b"] = float(input("Enter length of side b: "))
        params["c"] = float(input("Enter length of side c: "))
    elif shape == "Heptagon":
        params["side"] = float(input("Enter side length of heptagon: "))
    return params

def show_advantage(shape):
    if shape == "Square":
        print("Square: Excellent for cleaning corners and wall edges of standard rooms.")
    elif shape == "Circle":
        print("Circle: Moves smoothly, less likely to jam—great for open spaces.")
    elif shape == "Triangle":
        print("Triangle: Easily reaches tight spots and corners, but limited coverage.")
    elif shape == "Heptagon":
        print("Heptagon: More sides, good for complex layouts and edge cleaning.")

def main():
    while True:
        print("\nSelect Vacuum Cleaner Shape:")
        print("1. Square")
        print("2. Circle")
        print("3. Triangle")
        print("4. Heptagon")
        print("5. Exit")
        shapes = ["Square", "Circle", "Triangle", "Heptagon"]
        choice = int(input("Enter option (1-5): "))
        if choice == 5:
            print("Exiting vacuum cleaner program.")
            break
        if choice not in [1,2,3,4]:
            print("Invalid option. Try again.")
            continue

        shape = shapes[choice-1]
        params = get_params(shape)
        distance = calculate_distance(shape, params)
        print(f"Distance (Perimeter) for {shape}: {distance:.2f}")
        show_advantage(shape)

        while True:
            print("\nSelect command option:")
            print("1. Start")
            print("2. Stop")
            print("3. Left")
            print("4. Right")
            print("5. Dock")
            command_map = {
                1: "start",
                2: "stop",
                3: "left",
                4: "right",
                5: "dock"
            }
            cmd_choice = int(input("Enter command option (1-5): "))
            if cmd_choice not in command_map:
                print("Unknown command! Try again.")
                continue
            command = command_map[cmd_choice]
            if command == "start":
                print(f"{shape} Vacuum Cleaner: Starting Cleaning")
            elif command == "stop":
                print(f"{shape} Vacuum Cleaner: Stopping Cleaning. Returning to main menu.")
                break
            elif command == "left":
                print(f"{shape} Vacuum Cleaner: Moving Left")
            elif command == "right":
                print(f"{shape} Vacuum Cleaner: Moving Right")
            elif command == "dock":
                print(f"{shape} Vacuum Cleaner: Docking")

if __name__ == "__main__":
    main()
