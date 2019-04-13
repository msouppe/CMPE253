import java.io.File;
import java.util.concurrent.TimeUnit;

public class ClientTest {
    public static void main(String args[]) throws  Exception{
        SDNClient.leaderElect(4, 0, new File("./l1.txt"));
        SDNClient.leaderElect(4, 0, new File("./l1.txt"));
        SDNClient.leaderElect(4, 0, new File("./l1.txt"));
        SDNClient.leaderElect(4, 0, new File("./l1.txt"));

        TimeUnit.SECONDS.sleep(10);
//        SDNClient.leaderElect(5, 100, new File("./l1.txt"));

    }
}
