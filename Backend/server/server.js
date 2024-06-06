/**
 * Main server script for handling API requests, WebSocket connections, and data persistence.
 */

const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const WebSocket = require("ws");
const automerge = require("@automerge/automerge");
const uploadRoutes = require("./api/routes/uploadRoutes");
const transcriptRoutes = require("./api/routes/transcriptRoutes");
const speechToScriptPointerRoutes = require("./api/routes/speechToScriptPointerRoutes");
const performerTrackerRoutes = require("./api/routes/performerTrackerRoutes");
const errorHandler = require("./api/middlewares/errorHandler");

const cuesFilePath = path.join(__dirname, "storage", "cues", "cues.json");

const app = express();
app.use(cors());
app.use(express.json({ limit: "100mb" }));

let doc = automerge.init();
const clients = new Set();

// Initialize document or load existing state from cues.json
if (fs.existsSync(cuesFilePath)) {
  const savedState = fs.readFileSync(cuesFilePath);
  doc = automerge.load(savedState);
} else {
  doc = automerge.change(doc, (d) => {
    d.annotations = [];
  });
  saveCues();
}

/**
 * Save cues to the filesystem.
 */
function saveCues() {
  try {
    fs.mkdirSync(path.dirname(cuesFilePath), { recursive: true });
    const state = automerge.save(doc);
    fs.writeFileSync(cuesFilePath, state);
  } catch (error) {
    console.error("Failed to save cues:", error);
  }
}

// Register API routes
app.use("/api", uploadRoutes);
app.use("/api", transcriptRoutes);
app.use("/api", speechToScriptPointerRoutes);
app.use("/api", performerTrackerRoutes);

/**
 * Get annotations from the document.
 */
app.get("/api/cues", (req, res) => {
  const annotations = doc.annotations.map(convertTagsToList);
  res.status(200).json({ annotations });
});

/**
 * Get server status.
 */
app.get("/status", (req, res) => {
  res.status(200).json({ status: "running" });
});

// Register error handler middleware
app.use(errorHandler);

const PORT = 4000;
const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

const wss = new WebSocket.Server({ server });

/**
 * Broadcast changes to all connected clients.
 *
 * @param {Array} changes - List of changes to broadcast.
 */
function broadcastChanges(changes) {
  const message = JSON.stringify({ changes });
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message, (err) => {
        if (err) {
          console.error("Failed to send message:", err);
        }
      });
    }
  });
}

wss.on("connection", (ws) => {
  clients.add(ws);

  ws.on("close", () => {
    clients.delete(ws);
  });

  ws.on("message", (message) => {
    try {
      const data = JSON.parse(message);
      if (data && data.changes) {
        const newDoc = automerge.change(doc, (d) => {
          if (!d.annotations) d.annotations = [];
          data.changes.forEach((change) => {
            change.annotation = convertTagsToList(change.annotation);
            switch (change.type) {
              case "add":
                d.annotations.push(change.annotation);
                break;
              case "update":
                const index = d.annotations.findIndex(
                  (a) => a.id === change.annotation.id
                );
                if (
                  index !== -1 &&
                  change.timestamp >= (d.annotations[index].timestamp || 0)
                ) {
                  Object.keys(change.annotation).forEach((key) => {
                    if (
                      typeof change.annotation[key] === "object" &&
                      change.annotation[key] !== null
                    ) {
                      d.annotations[index][key] = {
                        ...d.annotations[index][key],
                        ...change.annotation[key],
                      };
                    } else {
                      d.annotations[index][key] = change.annotation[key];
                    }
                  });
                  d.annotations[index].timestamp = change.timestamp;
                }
                break;
              case "delete":
                const deleteIndex = d.annotations.findIndex(
                  (a) => a.id === change.annotation.id
                );
                if (deleteIndex !== -1) {
                  d.annotations.splice(deleteIndex, 1);
                }
                break;
            }
          });
        });

        doc = newDoc; // Assign the changed document
        saveCues();
        broadcastChanges(data.changes);
        ws.send(
          JSON.stringify({ ack: data.changes.map((change) => change.id) })
        );
      }
    } catch (error) {
      console.error("Failed to process message:", error);
    }
  });
});

/**
 * Convert annotation tags to a list if they are an object.
 *
 * @param {Object} annotation - The annotation to convert.
 * @returns {Object} The converted annotation.
 */
function convertTagsToList(annotation) {
  if (
    annotation.tags &&
    typeof annotation.tags === "object" &&
    !Array.isArray(annotation.tags)
  ) {
    annotation.tags = Object.values(annotation.tags);
  }
  return annotation;
}
