//package parser;


import java.io.*;
import java.util.Scanner;
import java.util.HashMap;
import java.util.*;
//import org.apache.commons.io.input.ReversedLinesFileReader;
//`import parser.Results_Obj;


public class Get_Optimal_K {

    public static void main(String[] args) {

        String Input_Path = "";
	int N = 0;
	int RF = 0;
	int CL = 0;
	double H_pre = 0.0d;
	double H_post = 0.0d;
	double T_switch = 0.0;
	double Theta = 0.0d;
	double predictedTime = 0.0d;
	//String Output_File = "";
	if(args.length > 6){

		N = Integer.parseInt(args[0]);
		RF = Integer.parseInt(args[1]);
		CL = Integer.parseInt(args[2]);

	 	H_pre = Double.parseDouble(args[3]);
		H_post = Double.parseDouble(args[4]);
		T_switch = Double.parseDouble(args[5]);
		Theta = Double.parseDouble(args[6]);
		predictedTime = Double.parseDouble(args[7]);
	}
    
 	int K_max = RF - CL;
	boolean found_k = false;
	for(int k = 2 ; k > 0 ; k--)
	{
		Double T_estimated = getSwitchMinTime(N,k,H_post,H_pre,T_switch);
		System.out.println("Estimated: " + T_estimated); 
		if(T_estimated < predictedTime)
		{
			//System.out.println("Found K = " + k + " Estimated time : " + T_estimated);	
			System.out.println("1" + " with k = " + k);
			found_k = true;
			break;
		}
	}
	if(!found_k)
	{
		//System.out.println("Found K = " + -1); //no reconfiguration
		System.out.println("-1");
	}
    }

    public static Double getProbabilityWorkload(Double T_estimated)
    {
	return 1.0d;	
    }	    
	
    public static Double getSwitchMinTime(int N, int K, double H_post, double H_pre, double T_switch)
    {
	
	int Steps = 0;
	Double Cost = 0.0d;
	Double Benefit = 0.0d;
	int L = (int) Math.ceil(N/K);
	double delta_ops = H_post - H_pre;
	for(int i = 0 ; i < L; i++)
	{
		Benefit += (i-1) * (K / (double)N) * delta_ops;		
		Cost += (K / (double)N) * H_pre;
	
		if(Benefit >= Cost)
		{
			return (i * T_switch);
		}
	}
	double t_stable = 0;
	if(Benefit < Cost)
	{
		t_stable = (Cost - Benefit) * T_switch / delta_ops;
	}

	return (t_stable + L * T_switch);
	
    }
}
