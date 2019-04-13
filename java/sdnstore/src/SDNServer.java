import java.io.*;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.logging.Level;
import java.util.logging.Logger;

import bftsmart.tom.MessageContext;
import bftsmart.tom.ServiceReplica;
import bftsmart.tom.server.defaultservices.DefaultSingleRecoverable;

public class SDNServer extends DefaultSingleRecoverable {

    private String nibByteArray = "{}";
    private long leader;
    private long timestamp;
    private Logger logger;
    private File nib;

    public SDNServer(int id, File nibPath) {
        logger = Logger.getLogger(SDNServer.class.getName());
        nib = nibPath;
        timestamp = -1;
        leader = 0;
        new ServiceReplica(id, this, this);
    }

    @SuppressWarnings("unchecked")
    @Override
    public byte[] appExecuteOrdered(byte[] command, MessageContext msgCtx) {
        byte[] reply = null;
        boolean hasReply = false;
        try (ByteArrayInputStream byteIn = new ByteArrayInputStream(command);
             ObjectInput objIn = new ObjectInputStream(byteIn);
             ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
             ObjectOutput objOut = new ObjectOutputStream(byteOut);) {

            int request_type  = (int)objIn.readObject();
            if(request_type == 0) { // leader_election

                int id = (int)objIn.readObject();
                //System.out.println("SDNserver.jar ID ::::"+id);
                long received_ts = (long)objIn.readObject();
                //System.out.println("SDNserver.jar timestamp ::::"+received_ts);
                if(timestamp == -1 || leader == id){
                    leader = id;
                    timestamp = received_ts;
                }
                else{
                    if(received_ts - timestamp >  1){
                        leader = id;
                        timestamp = received_ts;
                    }
                }
                objOut.writeObject(leader);
                objOut.flush();
                byteOut.flush();
                reply = byteOut.toByteArray();
                //System.out.println("SDNserver.jar leader ::::"+leader);
                //System.out.println("SDNserver.jar leader_ts ::::"+timestamp);
            }
            else if (request_type == 1){ // Transfering network State
                boolean status = false;
                nibByteArray = (String)objIn.readObject();
                status = true;
                objOut.writeObject(status);
                objOut.flush();
                byteOut.flush();
                reply = byteOut.toByteArray();
            }
            else{
                String nib_result = nibByteArray;
                objOut.writeObject(nib_result);
                objOut.flush();
                byteOut.flush();
                reply = byteOut.toByteArray();
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Ocurred during map operation execution", e);
        }
        return reply;
    }

    @SuppressWarnings("unchecked")
    @Override
    public byte[] appExecuteUnordered(byte[] command, MessageContext msgCtx) {
        byte[] reply = null;
        boolean hasReply = false;

        try (ByteArrayInputStream byteIn = new ByteArrayInputStream(command);
             ObjectInput objIn = new ObjectInputStream(byteIn);
             ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
             ObjectOutput objOut = new ObjectOutputStream(byteOut);) {

        } catch (Exception e) {
            logger.log(Level.SEVERE, "Ocurred during map operation execution", e);
        }

        return reply;
    }


    @Override
    public byte[] getSnapshot() {
        try (ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
             ObjectOutput objOut = new ObjectOutputStream(byteOut)) {
            objOut.writeObject(nibByteArray);
            objOut.writeObject(leader);
            objOut.writeObject(timestamp);
            return byteOut.toByteArray();
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error while taking snapshot", e);
        }
        return new byte[0];
    }

    @SuppressWarnings("unchecked")
    @Override
    public void installSnapshot(byte[] state) {
        try (ByteArrayInputStream byteIn = new ByteArrayInputStream(state);
             ObjectInput objIn = new ObjectInputStream(byteIn)) {
            nibByteArray = (String) objIn.readObject();
            leader = (int) objIn.readObject();
            timestamp = (long) objIn.readObject();
        } catch (IOException | ClassNotFoundException e) {
            logger.log(Level.SEVERE, "Error while installing snapshot", e);
        }
    }
}