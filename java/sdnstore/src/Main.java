import bftsmart.demo.listvalue.BFTList;

import java.io.File;
import java.nio.file.Files;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) throws Exception{
       if(args.length == 0){
           System.out.println("Please provide valid arguments");
           return;
       }
       else{
           File nib;
           int id;
           switch (args[0]){
               case "-server":
                   id = Integer.parseInt(args[1]);
                   nib = new File(args[2]);
                   new SDNServer(id, nib);
                   break;
               case "-client":
                   id = Integer.parseInt(args[1]);
                   if(args[2].equals("1")){
                       nib = new File(args[3]);
                       Scanner input = new Scanner(nib);
                       byte[] nibByteArray = Files.readAllBytes(nib.toPath());
                       SDNClient.BFTCommit(id, nibByteArray);
                   }
                   else{
                       int c_id = Integer.parseInt(args[3]);
                       System.out.println("main.jar :::: calling leader election");
                       File leader_file = new File(args[4]+"/leader.txt");
                       long timestamp = System.currentTimeMillis() / 1000L;
                       SDNClient.leaderElect(c_id, timestamp,leader_file);
                   }
                   break;
               default:
                   System.out.println("Please provide valid arguments");
           }
       }
    }
}
