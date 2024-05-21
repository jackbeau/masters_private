package broker;

import com.hivemq.embedded.EmbeddedHiveMQ;
import com.hivemq.embedded.EmbeddedHiveMQBuilder;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class EmbeddedMQTT {
    private static final Logger LOGGER = LoggerFactory.getLogger(EmbeddedMQTT.class);

    private final EmbeddedHiveMQBuilder embeddedHiveMQBuilder;
    private final Path basePath;
    private final Path dataPath;
    private final Path configPath;
    private final Path extensionsPath;
    private EmbeddedHiveMQ hiveMQ;
    private boolean serverRunning;

    public EmbeddedMQTT(String configFolder) throws IOException {
        this.basePath = configFolder != null ? Path.of(configFolder) : Path.of("mqtt-embedded");
        dataPath = this.basePath.resolve("data");
        configPath = this.basePath.resolve("conf");
        extensionsPath = this.basePath.resolve("extensions");

        Files.createDirectories(dataPath);
        Files.createDirectories(configPath);
        Files.createDirectories(extensionsPath);

        // Configure HiveMQ builder
        embeddedHiveMQBuilder = EmbeddedHiveMQ.builder()
                .withDataFolder(dataPath.toAbsolutePath())
                .withConfigurationFolder(configPath.toAbsolutePath())
                .withExtensionsFolder(extensionsPath.toAbsolutePath());
    }

    public void startServer() {
        try {
            hiveMQ = embeddedHiveMQBuilder.build();
            hiveMQ.start().join();
            serverRunning = true;
            LOGGER.info("Embedded MQTT server started successfully.");
        } catch (Exception ex) {
            LOGGER.error("Failed to start embedded MQTT server.", ex);
            serverRunning = false;
        }
    }

    public void stopServer() {
        if (hiveMQ != null) {
            try {
                hiveMQ.stop().join();
                hiveMQ.close();
            } catch (Exception e) {
                LOGGER.error("Failed to stop embedded MQTT server.", e);
            }
            hiveMQ = null; // Reset hiveMQ instance
            serverRunning = false;
            LOGGER.info("Embedded MQTT server stopped.");
        }
    }

    public boolean isServerRunning() {
        return serverRunning;
    }
}
