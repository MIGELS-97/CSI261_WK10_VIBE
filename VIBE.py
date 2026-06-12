import sys
import termios
import tty
from typing import List

FILE_NAME = "student_grades.txt"


class Student:
    """Represents one student record with scores, average, and grade."""

    def __init__(self, name: str, student_id: str, test1: float, test2: float, test3: float) -> None:
        self.name = name
        self.id = student_id
        self.test1 = round(test1, 2)
        self.test2 = round(test2, 2)
        self.test3 = round(test3, 2)
        self.average = round(self.calculate_average(self.test1, self.test2, self.test3), 2)
        self.grade = self.get_letter_grade(self.average)

    @staticmethod
    def calculate_average(test1: float, test2: float, test3: float) -> float:
        return (test1 + test2 + test3) / 3

    @staticmethod
    def get_letter_grade(average: float) -> str:
        if average >= 90:
            return "A"
        if average >= 80:
            return "B"
        if average >= 70:
            return "C"
        if average >= 60:
            return "D"
        return "F"

    def to_row(self) -> List[str]:
        return [
            self.name,
            self.id,
            f"{self.test1:.2f}",
            f"{self.test2:.2f}",
            f"{self.test3:.2f}",
            f"{self.average:.2f}",
            self.grade,
        ]

    def to_line(self) -> str:
        return f"{self.name}|{self.id}|{self.test1:.2f}|{self.test2:.2f}|{self.test3:.2f}|{self.average:.2f}|{self.grade}"

    @classmethod
    def from_line(cls, line: str) -> "Student":
        parts = line.split("|")
        if len(parts) != 7:
            raise ValueError("Invalid student record")
        name, student_id, test1, test2, test3, average, grade = parts
        student = cls(name, student_id, float(test1), float(test2), float(test3))
        student.average = round(float(average), 2)
        student.grade = grade
        return student




def clear_screen() -> None:
    """Clear the terminal screen for a cleaner interface."""
    print("\033[2J\033[H", end="")



def read_single_key() -> str:
    """Read a single key press from the terminal, including Escape."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key



def read_menu_choice() -> str:
    """Read a menu selection from either a real terminal or a piped input session."""
    if not sys.stdin.isatty():
        return input("Enter your choice: ").strip()
    return read_single_key()





def print_section(title: str) -> None:
    """Print a clearly labeled section header."""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)



def load_students(filename: str) -> List[Student]:
    """Load students from a pipe-delimited file."""
    students: List[Student] = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    students.append(Student.from_line(line))
                except ValueError:
                    print(f"Skipping invalid record on line {line_number}.")
    except FileNotFoundError:
        print("No existing file found. A new file will be created when you save.")
    except OSError as error:
        print(f"Error loading records: {error}")
    return students



def save_students(students: List[Student], filename: str) -> None:
    """Save all student records to a pipe-delimited file."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for student in students:
                file.write(student.to_line() + "\n")
        print(f"Records saved to {filename}.")
    except OSError as error:
        print(f"Error saving records: {error}")



def add_student(students: List[Student]) -> None:
    """Prompt for student data and add a new record."""
    print_section("Add Student")
    name = input("Enter student name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    student_id = input("Enter student ID: ").strip()
    if not student_id:
        print("ID cannot be empty.")
        return

    while True:
        try:
            test1 = float(input("Enter test 1 score: ").strip())
            test2 = float(input("Enter test 2 score: ").strip())
            test3 = float(input("Enter test 3 score: ").strip())
            break
        except ValueError:
            print("Please enter numeric scores.")

    student = Student(name, student_id, test1, test2, test3)
    students.append(student)
    save_students(students, FILE_NAME)
    print(f"Student {name} added successfully.")



def display_students(students: List[Student]) -> None:
    """Display all students in a formatted table."""
    print_section("Student Records")
    if not students:
        print("No student records to display.")
        return

    headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    rows = [student.to_row() for student in students]

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def print_row(values: List[str]) -> None:
        print("| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(values)) + " |")

    print_row(headers)
    print("-" * (sum(widths) + 3 * len(widths) + 1))
    for row in rows:
        print_row(row)




def display_class_statistics(students: List[Student]) -> None:
    """Display highest, lowest, and class average."""
    print_section("Class Statistics")
    if not students:
        print("No student records to analyze.")
        return

    highest = max(students, key=lambda item: item.average)
    lowest = min(students, key=lambda item: item.average)
    class_average = round(sum(student.average for student in students) / len(students), 2)

    print(f"Highest average: {highest.name} ({highest.average:.2f})")
    print(f"Lowest average: {lowest.name} ({lowest.average:.2f})")
    print(f"Class average: {class_average:.2f}")



def search_student(students: List[Student]) -> None:
    """Search for a student by name in a case-insensitive way."""
    print_section("Search Student")
    if not students:
        print("No student records available to search.")
        return

    name_query = input("Enter a student name to search: ").strip().lower()
    matches = [student for student in students if name_query in student.name.lower()]

    if not matches:
        print("No matching student found.")
        return

    print("Matching students:")
    for student in matches:
        print(f"{student.name} (ID: {student.id}) - Avg: {student.average:.2f}, Grade: {student.grade}")




def show_menu() -> None:
    print_section("Student Grade Calculator")
    print("Choose an option:")
    print("1. Add student")
    print("2. Display all students")
    print("3. Search student")
    print("4. Show class statistics")
    print("5. Save records")
    print("6. Exit")
    print("\nPress ESC to exit at any time.")




def main() -> None:
    """Run the interactive student grade calculator."""
    clear_screen()
    students = load_students(FILE_NAME)
    print("Loaded student grade records.")

    while True:
        show_menu()
        choice = read_menu_choice()
        if choice == "\x1b":
            print("\nExiting program. Goodbye!")
            save_students(students, FILE_NAME)
            break

        if choice == "1":
            add_student(students)
        elif choice == "2":
            display_students(students)
        elif choice == "3":
            search_student(students)
        elif choice == "4":
            display_class_statistics(students)
        elif choice == "5":
            save_students(students, FILE_NAME)
        elif choice == "6":
            print("\nExiting program. Goodbye!")
            save_students(students, FILE_NAME)
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()



