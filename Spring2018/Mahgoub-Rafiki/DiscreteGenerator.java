/**                                                                                                                                                                                
 * Copyright (c) 2010 Yahoo! Inc. All rights reserved.                                                                                                                             
 *                                                                                                                                                                                 
 * Licensed under the Apache License, Version 2.0 (the "License"); you                                                                                                             
 * may not use this file except in compliance with the License. You                                                                                                                
 * may obtain a copy of the License at                                                                                                                                             
 *                                                                                                                                                                                 
 * http://www.apache.org/licenses/LICENSE-2.0                                                                                                                                      
 *                                                                                                                                                                                 
 * Unless required by applicable law or agreed to in writing, software                                                                                                             
 * distributed under the License is distributed on an "AS IS" BASIS,                                                                                                               
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or                                                                                                                 
 * implied. See the License for the specific language governing                                                                                                                    
 * permissions and limitations under the License. See accompanying                                                                                                                 
 * LICENSE file.                                                                                                                                                                   
 */

package com.yahoo.ycsb.generator;
import java.io.*;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Scanner;
import java.util.HashMap;
import static java.util.Objects.requireNonNull;
//import SequenceCountPair;
import com.yahoo.ycsb.Utils;
import java.util.Timer;
import java.util.TimerTask;

/**
 * Generates a distribution by choosing from a discrete set of values.
 */
public class DiscreteGenerator extends Generator<String>
{
	private static class Pair
	{
		private double _weight;
		private String _value;

		Pair(double weight, String value)
		{
			_weight=weight;
			_value = requireNonNull(value);
		}
	}

	private final Collection<Pair> _values = new ArrayList<>();
	private String _lastvalue;

	SequenceCountPair currentSequenceCountPair = new SequenceCountPair();

	HashMap<Integer,SequenceCountPair> allSequencesWLDictionary = new HashMap<Integer,SequenceCountPair>();
	ArrayList<Double> rr_sequence_list = new ArrayList<Double>();
	ArrayList<Integer> perdios_sequence_list = new ArrayList<Integer>();
	int scenario_index = 0;
	//int count = 0;
	//int index = -1;
	//ArrayList<Integer> count_list = new ArrayList<Integer>();
	//ArrayList<String> sequence_list = new ArrayList<String>();
	
	public void getSequencesMap()
	{
		try
		{
			File folder = new File("//home//ubuntu//YCSB-master//core//src//main//java//com//yahoo//ycsb//generator//Out_Train_RR//dynmaic_split");
			File[] listOfFiles = folder.listFiles();	
			for (File file : listOfFiles) {
				SequenceCountPair newPair = new SequenceCountPair();

				String Name = file.getName(); //sequence_70_split
				String[] parts = Name.split("_");
				int key = Integer.parseInt(parts[1]);
				
				Scanner input = new Scanner(file);
				while (input.hasNext())
                	         {
        	                        String line = new String(input.nextLine());
	                                String[] parts2 = line.split("_");
        	                        if(parts2.length > 1)
	                                {
                	                       	 newPair.sequence_list.add(parts2[0]);
                        	              	 newPair.count_list.add(Integer.parseInt(parts2[1]));
                               		}
        	                 }
		
                	       	 input.close();
				 allSequencesWLDictionary.put(key,newPair);			
				 System.out.println("Added key: " + key);
				System.out.println("Added newPair: " + newPair);
			}
		}
		catch(Exception ex)
                {
                   ex.printStackTrace();
                }

	}
	
	public void getSequencesPeriods()
	{
		
		try
                {

			File file = new File("//home//ubuntu//YCSB-master//current_scenario");
			Scanner input = new Scanner(file);
			while (input.hasNext())
			{
				String line = new String(input.nextLine());
				System.out.println(line);
				String[] parts = line.split("\t");
				if(parts.length > 1)
       		                 {
					if(line.contains("rr"))
					{
						rr_sequence_list.add(Double.parseDouble(parts[1]));
					}
					else
					{
						perdios_sequence_list.add(Integer.parseInt(parts[1]));
					}
				}
			}
			input.close();
		}
                catch(Exception ex)
                {
                   ex.printStackTrace();
                }		
	}
	public DiscreteGenerator()
	{
		try
		{
			System.out.println("loading sequence data");
			getSequencesMap();

			System.out.println("loading scenarios");
			getSequencesPeriods();
			
			
			int currentKey = (int) (rr_sequence_list.get(scenario_index)*100);
			System.out.println("currentKey: " + currentKey);
			if( allSequencesWLDictionary.containsKey(currentKey))
			{
				currentSequenceCountPair = allSequencesWLDictionary.get(currentKey);
				if(currentSequenceCountPair == null)
               			{
                	        	 System.out.println("Null <<--");
		                }

				System.out.println("sequences size: " +  allSequencesWLDictionary.size());		
			}
			int sum_periods = 0;	
			for(int i = 0 ; i < perdios_sequence_list.size() -1 ; i++)
			{
				Timer timer = new Timer();
				sum_periods += perdios_sequence_list.get(i);
				timer.schedule(new RemindTask(i+1) , 1000*30*sum_periods);
			}		
			/*System.out.println("loading sequence data");
			//File file = new File("//home//ubuntu//YCSB-master//current_sequence");
			//Scanner input = new Scanner(file);
        		//while (input.hasNext())
               		 {
				String line = new String(input.nextLine());
				String[] parts = line.split("_");
				if(parts.length > 1)
				{
					sequence_list.add(parts[0]);
					count_list.add(Integer.parseInt(parts[1]));
				}			
 			}

			input.close();
			_lastvalue=null;*/
		}
		catch(Exception ex) 
		{
	           ex.printStackTrace();
     	        }
	}
	class RemindTask extends TimerTask{
		int _index = 0;
		public	RemindTask(int index)
		{
			_index = index;
		} 
		public void run() {
			//Outer.this.scenario_index ++;
		      int currentKey = (int) (rr_sequence_list.get(_index)*100);
	              currentSequenceCountPair = allSequencesWLDictionary.get(currentKey);
	              int currentPeriod = 30*perdios_sequence_list.get(_index);
		      System.out.println("Switching_Configs_TO: " + rr_sequence_list.get(_index) + " for " + currentPeriod + " sec");
		      String hostIdSysEnvStr = System.getenv("HostID");
		      try{			
		      //String[] env = {"PATH=/bin:/usr/bin/"};
	              //String cmd = "mkdir /home/ubuntu/config_switch/" + rr_sequence_list.get(_index) + ".txt";  //e.g test.sh -dparam1 -oout.txt
	              //Double currentPeriod = 30*perdios_sequence_list.get(_index);
		      //String cmd = "echo " + currentPeriod + " >/home/ubuntu/config_switch/" + rr_sequence_list.get(_index) + ".txt";
		        System.out.println("Writing " + currentPeriod + " to file " + "/home/ubuntu/config_switch/"+ rr_sequence_list.get(_index) + ".txt");		     
                        //Process process = Runtime.getRuntime().exec(cmd, env);
			FileWriter fw = new FileWriter("/home/ubuntu/config_switch/"+ rr_sequence_list.get(_index) + ".txt");
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(currentPeriod);
			bw.close();
		      }
        	      catch(Exception ex)
	              {
                	   ex.printStackTrace();
                      }

		      //FileWriter fw = new FileWriter("/home/ubuntu/config_switch/rr.txt");
		      //BufferedWriter bw = new BufferedWriter(fw);
		      //bw.write(rr_sequence_list.get(_index));
		      //bw.close();
		      //fw.close();	
		      //Process p = Runtime.getRuntime().exec("ssh ");	     
		      //timer.cancel(); //Not necessary because we call System.exit
      			//System.exit(0); //Stops the AWT thread (and everything else)
    		}
  	}
	/**
	 * Generate the next string in the distribution.
	 */
	@Override
    public String nextValue()
	{
		if(currentSequenceCountPair == null)
		{
			 System.out.println("Null -->");
		}
		if(currentSequenceCountPair.count <= 0)
		{
			synchronized(this){
	
			currentSequenceCountPair.index++;
			if((currentSequenceCountPair.index >= currentSequenceCountPair.sequence_list.size()) || (currentSequenceCountPair.index >= currentSequenceCountPair.count_list.size()))
			{
				currentSequenceCountPair.index =0;
			}
			currentSequenceCountPair.count = currentSequenceCountPair.count_list.get(currentSequenceCountPair.index);
			currentSequenceCountPair.count--;
			String type = currentSequenceCountPair.sequence_list.get(currentSequenceCountPair.index);
			//System.out.println("type:" + type+":");
			if(type.trim().equals("select"))
			{
				return "READ";
			}		
			else
			{
				return "INSERT";
			}
			}
		}
		else
		{
			currentSequenceCountPair.count--;
			String type = currentSequenceCountPair.sequence_list.get(currentSequenceCountPair.index);
			//System.out.println("type:" + type+":");
			if(type.equals("select"))
                        {
                                return "READ";
                        }
                        else
                        {
                                return "INSERT";
                        }
                        //return type;
		}
/*		double sum=0;

		for (Pair p : _values)
		{
			sum+=p._weight;
		}

		double val=Utils.random().nextDouble();

		for (Pair p : _values)
		{
		    double pw = p._weight / sum;
			if (val < pw)
			{
				retu`rn p._value;
			}

			val -= pw;
		}
*/
		//throw new AssertionError("oops. should not get here.");

	}

	/**
	 * Return the previous string generated by the distribution; e.g., returned from the last nextString() call. 
	 * Calling lastString() should not advance the distribution or have any side effects. If nextString() has not yet 
	 * been called, lastString() should return something reasonable.
	 */
	@Override
    public String lastValue()
	{
		if (_lastvalue==null)
		{
			_lastvalue=nextValue();
		}
		return _lastvalue;
	}

	public void addValue(double weight, String value)
	{
		_values.add(new Pair(weight,value));
	}

}
