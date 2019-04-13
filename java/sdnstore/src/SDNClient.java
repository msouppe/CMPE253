import bftsmart.tom.ServiceProxy;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import static com.sun.xml.internal.ws.spi.db.BindingContextFactory.LOGGER;

public class SDNClient{
    private static ServiceProxy serviceProxy;

    private static final Logger LOGGER = Logger.getLogger(SDNClient.class.getName());

    public SDNClient(int ClientId) {

    }

    public static void BFTCommit(int id, byte[] nib){
        serviceProxy = new ServiceProxy(id);
        boolean result;
        try (ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
             ObjectOutput objOut = new ObjectOutputStream(byteOut)) {
            objOut.writeObject(1);
            objOut.writeObject(nib);
            objOut.flush();
            byteOut.flush();
            byte[] reply;
            try {
                reply = serviceProxy.invokeOrdered(byteOut.toByteArray());
                if (reply.length == 0)
                    throw new IOException();
            } catch (RuntimeException e) {
                LOGGER.log(Level.SEVERE, "Commit Failed: " + e.getLocalizedMessage(), e);
                return;
            }
            try (ByteArrayInputStream byteIn = new ByteArrayInputStream(reply);
                 ObjectInput objIn = new ObjectInputStream(byteIn)) {
                result = (boolean) objIn.readObject();
            }
        } catch (IOException | ClassNotFoundException e) {
            LOGGER.log(Level.SEVERE, "Exception generated while committing transaction" + e.getLocalizedMessage(), e);
        }
        serviceProxy.close();
        System.exit(0);
        return;
    }

    public static void leaderElect(int id, long timestamp, File leader_file){
        serviceProxy = new ServiceProxy(id);
        boolean result;
        try (ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
             ObjectOutput objOut = new ObjectOutputStream(byteOut)) {
            objOut.writeObject(0);
            objOut.writeObject(id);
            objOut.writeObject(timestamp);
            objOut.flush();
            byteOut.flush();
            byte[] reply;
            try {
                reply = serviceProxy.invokeOrdered(byteOut.toByteArray());
                if (reply.length == 0)
                    throw new Exception();
                    //leaderElect(id, timestamp, leader_file);
            } catch (Exception e) {
                LOGGER.log(Level.SEVERE, "Commit Failed: " + e.getLocalizedMessage(), e);
                return;
            }
            try (ByteArrayInputStream byteIn = new ByteArrayInputStream(reply);
                 ObjectInput objIn = new ObjectInputStream(byteIn)) {
                long leader = (long) objIn.readObject();
                //System.out.println("SDNclient.jar :::: leader election result :"+leader);
                String writeLeaderString = leader+"";
                try {
                    Files.write(leader_file.toPath(), writeLeaderString.getBytes());
                } catch (IOException e) {
                    e.printStackTrace();
                }
                System.out.println(leader);
            }
        } catch (IOException | ClassNotFoundException e) {
            LOGGER.log(Level.SEVERE, "Exception generated while committing transaction" + e.getLocalizedMessage(), e);
        }
        serviceProxy.close();

    }
}