

import java.io.*;
import java.util.Scanner;
import java.util.HashMap;
import java.util.*;
//`import parser.Results_Obj;


public class getValue{

    public static void main(String[] args) {
	try{	File file = new File(args[0]);
	Scanner input = new Scanner(file);
	while (input.hasNext())
        {
		System.out.println(input.nextLine());
		break;
	}
	input.close();
	}
	catch(Exception ex) {
       
            ex.printStackTrace();
	}
    }
}
