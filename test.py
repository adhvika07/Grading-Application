import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, simpledialog, StringVar, Radiobutton
import sqlite3

def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            classroom_id INTEGER NOT NULL,
            overall_grade REAL,
            FOREIGN KEY (classroom_id) REFERENCES classrooms (id),
            UNIQUE(name, classroom_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            max_score INTEGER NOT NULL,
            score INTEGER NOT NULL,
            percentage REAL,
            letter_grade TEXT,
            assignment_type TEXT NOT NULL,
            student_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    conn.commit()
    conn.close()

def calculate_letter_grade(percentage):
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grading System")
        self.conn = sqlite3.connect('school.db')
        self.cursor = self.conn.cursor()
        
        tk.Label(root, text="Classroom Name:").pack()
        self.class_name_entry = tk.Entry(root)
        self.class_name_entry.pack()

        tk.Button(root, text="Add Classroom", command=self.add_classroom).pack()

        tk.Label(root, text="Student Name:").pack()
        self.student_name_entry = tk.Entry(root)
        self.student_name_entry.pack()

        tk.Button(root, text="Add Student to Classroom", command=self.add_student).pack()

        tk.Label(root, text="Assignment Name:").pack()
        self.assignment_name_entry = tk.Entry(root)
        self.assignment_name_entry.pack()

        tk.Label(root, text="Assignment Type:").pack()
        self.assignment_type_var = StringVar(value="Homework")
        Radiobutton(root, text="Homework", variable=self.assignment_type_var, value="Homework").pack()
        Radiobutton(root, text="Test", variable=self.assignment_type_var, value="Test").pack()

        tk.Label(root, text="Max Score:").pack()
        self.max_score_entry = tk.Entry(root)
        self.max_score_entry.pack()

        tk.Label(root, text="Score:").pack()
        self.score_entry = tk.Entry(root)
        self.score_entry.pack()

        tk.Button(root, text="Add  and Grade Assignment", command=self.add_edit_assignment).pack()

        tk.Button(root, text="View Student Grades", command=self.view_grades).pack()

        tk.Button(root, text="View Class Grades", command=self.view_class_grades).pack()

        tk.Button(root, text="View All Student Details", command=self.view_all_students).pack()

        tk.Button(root, text="Edit Assignment", command=self.edit_assignment).pack()

        tk.Button(root, text="Delete Assignment", command=self.delete_assignment).pack()

    def view_all_students(self):
    
        self.cursor.execute('''
            SELECT c.name AS classroom_name, s.name AS student_name, a.name AS assignment_name,
                   a.assignment_type, a.score, a.max_score, a.percentage, a.letter_grade, s.overall_grade
            FROM classrooms c
            JOIN students s ON c.id = s.classroom_id
            LEFT JOIN assignments a ON s.id = a.student_id
            ORDER BY c.name, s.name
        ''')
        rows = self.cursor.fetchall()


        if rows:
            details_window = Toplevel(self.root)
            details_window.title("All Students Details")
            tree = ttk.Treeview(details_window, columns=("Classroom", "Student", "Assignment", "Type", "Score", "Percentage", "Grade", "Overall Grade"), show="headings")
            tree.heading("Classroom", text="Classroom")
            tree.heading("Student", text="Student")
            tree.heading("Assignment", text="Assignment")
            tree.heading("Type", text="Type")
            tree.heading("Score", text="Score")
            tree.heading("Percentage", text="Percentage")
            tree.heading("Grade", text="Grade")
            tree.heading("Overall Grade", text="Overall Grade")
            tree.pack(fill="both", expand=True)

            for classroom_name, student_name, assignment_name, assignment_type, score, max_score, percentage, letter_grade, overall_grade in rows:
                percentage_str = f"{percentage:.2f}%" if percentage is not None else "N/A"
                score_str = score if score is not None else "N/A"
                max_score_str = max_score if max_score is not None else "N/A"
                grade_str = letter_grade if letter_grade else "N/A"
                assignment_str = assignment_name if assignment_name else "N/A"
                overall_grade_str = f"{overall_grade:.2f}%" if overall_grade is not None else "N/A"
                tree.insert("", "end", values=(classroom_name, student_name, assignment_str, assignment_type, score_str, max_score_str, percentage_str, grade_str, overall_grade_str))
        else:
            messagebox.showinfo("Info", "No data found.")



    def calculate_overall_grade(self, student_id):
        total_homework_score = 0
        num_homework_assignments = 0
        total_test_score = 0
        num_tests = 0


        self.cursor.execute('''
            SELECT assignment_type, score, max_score
            FROM assignments
            WHERE student_id = ?
        ''', (student_id,))
        assignments = self.cursor.fetchall()


        for assignment_type, score, max_score in assignments:
            if assignment_type == "Homework":
                total_homework_score += (score / max_score) * 100
                num_homework_assignments += 1
            elif assignment_type == "Test":
                total_test_score += (score / max_score) * 100
                num_tests += 1

        avg_homework = total_homework_score / num_homework_assignments if num_homework_assignments > 0 else 0
        avg_test = total_test_score / num_tests if num_tests > 0 else 0


        if num_homework_assignments > 0 and num_tests == 0:
            overall_grade = avg_homework
        elif num_tests > 0 and num_homework_assignments == 0:
            overall_grade = avg_test
        else:
            overall_grade = 0.7 * avg_homework + 0.3 * avg_test

        # if avg_homework is not None and avg_test is not None:
        #     overall_grade = 0.7 * avg_homework + 0.3 * avg_test
        # elif avg_homework is not None:
        #     overall_grade = avg_homework
        # elif avg_test is not None:
        #     overall_grade = avg_test
        # else:
        #     overall_grade = None

       
        self.cursor.execute('''
            UPDATE students
            SET overall_grade = ?
            WHERE id = ?
        ''', (overall_grade, student_id))
        self.conn.commit()

    def add_edit_assignment(self):
        student_name = self.student_name_entry.get()
        assignment_name = self.assignment_name_entry.get()
        assignment_type = self.assignment_type_var.get()

        try:
            max_score = int(self.max_score_entry.get())
            score = int(self.score_entry.get())

            if score < 0 or score > max_score:
                messagebox.showerror("Error", "Score has to be between 0 and max score.")
                return

            percentage = (score / max_score) * 100
            letter_grade = calculate_letter_grade(percentage)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for score and max score.")
            return

        self.cursor.execute('SELECT id FROM students WHERE name = ?', (student_name,))
        student_id = self.cursor.fetchone()
        print(student_id)
        if student_id:
            self.cursor.execute('''
                INSERT INTO assignments (name, max_score, score, percentage, letter_grade, assignment_type, student_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (assignment_name, max_score, score, percentage, letter_grade, assignment_type, student_id[0]))
            self.conn.commit()

            self.calculate_overall_grade(student_id[0])

            messagebox.showinfo("Info", f"Assignment '{assignment_name}' added/edited for student '{student_name}'. Grade: {letter_grade} ({percentage:.2f}%)")
        else:
            messagebox.showerror("Error", "Student not found.")


    def edit_assignment(self):
        student_name = simpledialog.askstring("Input", "Enter student name to edit assignment:", parent=self.root)
        assignment_name = simpledialog.askstring("Input", "Enter assignment name to edit:", parent=self.root)
        if not student_name or not assignment_name:
            messagebox.showinfo("Info", "Student name and Assignment name cannot be empty.")
            return

        new_score = simpledialog.askinteger("Input", "Enter new score:", parent=self.root)
        new_max_score = simpledialog.askinteger("Input", "Enter new max score:", parent=self.root)
        new_assignment_type = simpledialog.askstring("Input", "Enter new assignment type (Homework/Test):", parent=self.root)
        
        if new_score < 0 or new_score > new_max_score:
            messagebox.showerror("Error", "Score must be between 0 and the maximum score.")
            return
    
        new_percentage = (new_score / new_max_score) * 100
        new_letter_grade = calculate_letter_grade(new_percentage)

        self.cursor.execute('SELECT s.id FROM students s WHERE s.name = ?', (student_name,))
        student_id = self.cursor.fetchone()
        if student_id:
            self.cursor.execute('''
                UPDATE assignments
                SET max_score = ?, score = ?, percentage = ?, letter_grade = ?, assignment_type = ?
                WHERE name = ? AND student_id = ?
            ''', (new_max_score, new_score, new_percentage, new_letter_grade, new_assignment_type, assignment_name, student_id[0]))
            self.conn.commit()

            self.calculate_overall_grade(student_id[0])

            messagebox.showinfo("Info", f"Assignment '{assignment_name}' updated for student '{student_name}'. New Grade: {new_letter_grade} ({new_percentage:.2f}%)")
        else:
            messagebox.showerror("Error", "Student not found.")

    def delete_assignment(self):
        student_name = simpledialog.askstring("Input", "Enter student name to delete assignment:", parent=self.root)
        assignment_name = simpledialog.askstring("Input", "Enter assignment name to delete:", parent=self.root)
        if not student_name or not assignment_name:
            messagebox.showinfo("Info", "Student name and Assignment name cannot be empty.")
            return

        self.cursor.execute('SELECT s.id FROM students s WHERE s.name = ?', (student_name,))
        student_id = self.cursor.fetchone()
        if student_id:
            self.cursor.execute('DELETE FROM assignments WHERE name = ? AND student_id = ?', (assignment_name, student_id[0]))
            self.conn.commit()

            self.calculate_overall_grade(student_id[0])

            messagebox.showinfo("Info", f"Assignment '{assignment_name}' deleted for student '{student_name}'.")
            self.view_grades(student_name)
        else:
            messagebox.showerror("Error", "Student not found.")


    def view_grades(self, student_name=None):
        if not student_name:
            student_name = simpledialog.askstring("Input", "Enter student name to view grades:",
                                              parent=self.root)
        if student_name:
            self.cursor.execute('''
                SELECT a.name, a.assignment_type, a.score, a.percentage, a.letter_grade, s.overall_grade
                FROM assignments a
                JOIN students s ON a.student_id = s.id
                WHERE s.name = ?''', (student_name,))
            rows = self.cursor.fetchall()

            if rows:
                grade_window = Toplevel(self.root)
                grade_window.title(f"Grades for {student_name}")

                tree = ttk.Treeview(grade_window, columns=("Assignment Name", "Type", "Score", "Percentage", "Grade"), show="headings")
                tree.heading("Assignment Name", text="Assignment Name")
                tree.heading("Type", text="Type")
                tree.heading("Score", text="Score")
                tree.heading("Percentage", text="Percentage")
                tree.heading("Grade", text="Grade")
                tree.pack(fill="both", expand=True)

                for name, assignment_type, score, percentage, letter_grade, overall_grade in rows:
                    tree.insert("", "end", values=(name, assignment_type, score, f"{percentage:.2f}%", letter_grade))
                
                tk.Label(grade_window, text=f"Overall Grade: {overall_grade:.2f}%").pack()
            else:
                messagebox.showinfo("Info", "No grades found for this student.")
        else:
            messagebox.showinfo("Info", "Student name cannot be empty.")


    def view_class_grades(self):
        classroom_name = simpledialog.askstring("Input", "Enter classroom name to view grades:", parent=self.root)
        if classroom_name:
            self.cursor.execute('SELECT id FROM classrooms WHERE name = ?', (classroom_name,))
            classroom_id = self.cursor.fetchone()
            if classroom_id:
                self.cursor.execute('''
                SELECT s.name, s.overall_grade
                FROM students s
                WHERE s.classroom_id = ?
            ''', (classroom_id[0],))
                students = self.cursor.fetchall()
                grade_window = Toplevel(self.root)
                grade_window.title(f"Grades for Classroom {classroom_name}")

                tree = ttk.Treeview(grade_window, columns=("Student Name", "Overall Grade"), show="headings")
                tree.heading("Student Name", text="Student Name")
                tree.heading("Overall Grade", text="Overall Grade")
                tree.pack(fill="both", expand=True)
                
                if students:
                    for student_name, overall_grade in students:
                        overall_grade_str = f"{overall_grade:.2f}%" if overall_grade is not None else "Grade not calculated"
                        tree.insert("", "end", values=(student_name, overall_grade_str))
                else:
                    tk.Label(grade_window, text="No students found for this classroom.").pack()
            else:
                messagebox.showinfo("Info", "Classroom not found.")
        else:
            messagebox.showinfo("Info", "Classroom name cannot be empty.")



    def add_classroom(self):
        class_name = self.class_name_entry.get()
        if class_name:
            try:
                self.cursor.execute('INSERT INTO classrooms (name) VALUES (?)', (class_name,))
                self.conn.commit()
                messagebox.showinfo("Info", f"Classroom '{class_name}' added.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Classroom already exists.")

    def add_student(self):
        class_name = self.class_name_entry.get()
        student_name = self.student_name_entry.get()
        if not class_name or not student_name:
            messagebox.showerror("Error", "Classroom and Student names cannot be empty.")
            return
        self.cursor.execute('SELECT id FROM classrooms WHERE name = ?', (class_name,))
        classroom_id = self.cursor.fetchone()

        if classroom_id:
            try:
                self.cursor.execute('INSERT INTO students (name, classroom_id) VALUES (?, ?)', (student_name, classroom_id[0]))
                self.conn.commit()
                messagebox.showinfo("Info", f"Student '{student_name}' added to classroom '{class_name}'.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Student '{student_name}' already exists in classroom '{class_name}'.")
        else:
            messagebox.showerror("Error", "Classroom not found.")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = App(root)
    root.mainloop()

class Assignment:
    def __init__(self, name, max_score):
        self.name = name
        self.max_score = max_score

class Student:
    def __init__(self, name):
        self.name = name
        self.assignments = {}

    def add_assignment(self, assignment, score):
        if 0 <= score <= assignment.max_score:
            self.assignments[assignment.name] = score
        else:
            raise ValueError("Score out of range")

class Classroom:
    def __init__(self, name):
        self.name = name
        self.students = {}

    def add_student(self, student_name):
        self.students[student_name] = Student(student_name)

    def get_student(self, student_name):
        return self.students.get(student_name)

