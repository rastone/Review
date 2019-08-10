/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

package as11;

public class StudentExt extends Student {

	private String gradeType;
	
	public StudentExt (int iden, String n, double[] s, String gt) {
		super(iden, n, s);
		gradeType = gt;
	}

	public String findGrade() {
	    String grade = super.findGrade();
	    
	    if (gradeType.equalsIgnoreCase ("Credit")) {
	    	
	      if ((grade.equalsIgnoreCase ("A")) ||
	    	  (grade.equalsIgnoreCase ("B")) || 
	          (grade.equalsIgnoreCase ("C")) )
	            grade = "CR";
	      else
	            grade = "NCR";
	    }
	    return grade;
	}
	
	public String getGradeType() {
		return gradeType;
	}
	
}
