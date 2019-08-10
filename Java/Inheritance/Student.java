/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

package as11;

public class Student {

	private int id;
	private String name;
	private double[] examScores;
	
	public Student(int iden, String n, double[] s) {
		id = iden;
		name = n;
		examScores  = s; 
	}

	public String findGrade() {
		String grade;
		double sum, avg;
		sum = 0;
		
		for (int i = 0; i < examScores.length; i++)
			sum = sum + examScores[i];
		
		avg = sum / examScores.length;
		if (avg >= 90.0) grade = "A";
		else if (avg >= 80.0) grade = "B";
		else if (avg >= 70.0) grade = "C";
		else if (avg >= 60.0) grade = "D";
		else grade = "F";
		
		return grade;
	}

	public int getId() {
		return id;
	}

	public String getName() {
		return name;
	}
	
}
