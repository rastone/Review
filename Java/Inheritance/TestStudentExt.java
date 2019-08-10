/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

package as11;

import java.util.StringTokenizer;
import javax.swing.JOptionPane;

public class TestStudentExt {

	public static void main(String[] args) {
		
		String name, grade, gradeType, in, token;
	    int id, nStudents, nExams;
	    double[] scores;
	    
	    in = JOptionPane.showInputDialog("Enter number of students");
	    nStudents = Integer.parseInt(in);

	    // Create an array of nStudents references
	    StudentExt [] ste = new StudentExt [nStudents];
	    
	    // Create nStudents objects
	    for (int i = 0; i < ste.length; i++)
	    {
	      // Input one student data
	      in = JOptionPane.showInputDialog("Enter one student data");

	      // Tokenize student data using StringTokenizer
	       StringTokenizer stk = new StringTokenizer (in, ",");
	       
	       token = stk.nextToken().trim();
	       id = Integer.parseInt(token);
	       
	       name = stk.nextToken().trim();
	       token = stk.nextToken().trim();
	       
	       nExams = Integer.parseInt(token);
	       scores = new double[nExams];
	       
	       //populate scores array       
	       for (int j = 0; j < scores.length; j++) {
	    	   token = stk.nextToken().trim();
	    	   scores[j] = Double.parseDouble(token);
	       }
	       
	       gradeType = stk.nextToken().trim();

	      // Create Student objects
	      ste [i] = new StudentExt (id, name, scores, gradeType);
	    }

	    // Create 5 string references
	    String outA ="", outB ="",outC ="",outD ="",outF ="", outCR = "", outNCR = "";
	    
	    // Find student grades
	    for (int i = 0; i < ste.length; i++) {
	    	grade = ste[i].findGrade();
	    	
	    	if(grade.equalsIgnoreCase("A")) {
	    		outA += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" + "\n"; 
	    	}
	    	else if(grade.equalsIgnoreCase("B")) {
	    		outB += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" + "\n"; 
	    	}
	    	else if(grade.equalsIgnoreCase("C")) {
	    		outC += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" + "\n"; 
	    	}
	    	else if(grade.equalsIgnoreCase("D")) {
	    		outD += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" + "\n"; 
	    	} 
	    	else if (grade.equalsIgnoreCase("F")) {
	    		outF += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" +  "\n";
	    	}
	    	else if (grade.equalsIgnoreCase("CR")) {
	    		outCR += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" +  "\n";
	    	}
	    	else if (grade.equalsIgnoreCase("NCR")) {
	    		outNCR += ste[i].getId() + " " + ste[i].getName() + " " + "(" + grade + ")" +  "\n";
	    	}

	    }
	 
	    String outAll = outA+outB+outC+outD+outF+outCR+outNCR;
	    JOptionPane.showMessageDialog(null, outAll);
	    
	}
}
