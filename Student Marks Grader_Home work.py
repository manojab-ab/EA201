
def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"

def student_grading():
    num_subjects = int(input("How many subjects? "))

    subject_names = []
    for i in range(num_subjects):
        subject = input(f"Enter the name of subject {i + 1}: ")
        subject_names.append(subject)

    report_card = {}

    for subject in subject_names:
        marks = int(input(f"Enter marks for {subject} (out of 100): "))
        grade = calculate_grade(marks)
        report_card[subject] = {"Marks": marks, "Grade": grade}

    print("\n--- Student Report Card ---")
    for subject, info in report_card.items():
        print(f"{subject}: Marks = {info['Marks']}, Grade = {info['Grade']}")

    total_marks = sum(info["Marks"] for info in report_card.values())
    average = total_marks / num_subjects
    final_grade = calculate_grade(average)

    print(f"\nAverage Marks: {average:.2f}")
    print(f"Final Grade: {final_grade}")
    
student_grading()

