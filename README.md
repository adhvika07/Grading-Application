Created a full stack Grading application which allows you to Add students, Add classes, Add students to the class, Add Assignments for the class Categorized as Homework or Test Assignments as well as Grades the applications. Grades are calculated in both Letter Grade as well as Percentage grade. All this information is stored in a database and viewed whenever you want to using the View All students button.


The application page request you to enter a class, then you add the class which basically establishes the existence of the class being added to our database. Then we add a student to a particular class by speicfying the name of the student. We then add an assignment, the app allows you to specify whether its a Homework or Test type of assignment.


You then enter the total marks possible in the assignment and the marks obtained by the student. This is what helps us calculate the grade for the student for that partculat assignment for that particular class. By clicking on the "Calculate grade" button we get the grades for it.


I have incorporated a lot of error handling properties in this application such as confirming the exitence of the class, the student, an exception for negative or 0 marks being entered and trying to skip a particular step that is required in this process.
