package broker;

import java.io.IOException;

public class App {
    
    public static void main(String[] args) throws IOException {
        EmbeddedMQTT mqttServer = new EmbeddedMQTT(null);
        mqttServer.startServer();
        System.out.println("Stopping");
        // mqttServer.stopServer();
        // System.exit(0);
    }
}
