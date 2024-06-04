const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const WebSocket = require('ws');
const automerge = require('@automerge/automerge');
const { addMargin, performOCR, startSpeechToLine, stopSpeechToLine, startPerformerTracker, stopPerformerTracker } = require('./grpc/client/client');

const app = express();
app.use(cors());
app.use(express.json({ limit: '100mb' }));

const cuesFilePath = path.join(__dirname, 'storage', 'cues', 'cues.json');
let doc = automerge.init();
const clients = new Set();

if (fs.existsSync(cuesFilePath)) {
  const savedState = fs.readFileSync(cuesFilePath);
  doc = automerge.load(savedState);
} else {
  doc = automerge.change(doc, d => {
    d.annotations = [];
  });
  saveCues();
}

function saveCues() {
  try {
    fs.mkdirSync(path.dirname(cuesFilePath), { recursive: true });
    const state = automerge.save(doc);
    fs.writeFileSync(cuesFilePath, state);
  } catch (error) {
    console.error('Failed to save cues:', error);
  }
}

const upload = multer({ dest: 'server/storage/pdfs/' });

// Endpoint to upload PDF
app.post('/upload', upload.single('file'), async (req, res) => {
  const file = req.file;
  const marginSide = req.body.marginSide;

  try {
    // Add margin to the PDF
    const addMarginResponse = await addMargin(file.path, marginSide);

    // Perform OCR on the PDF
    const ocrResponse = await performOCR(addMarginResponse.file_path);

    // Extract the filename from the full file path
    const filename = path.basename(addMarginResponse.file_path);

    // Construct the full URL for the modified PDF
    const fullUrl = `${req.protocol}://${req.get('host')}/download/${filename}`;

    // Return the modified PDF and OCR text
    res.json({
      filename: file.filename,
      filepath: fullUrl,
      ocrText: ocrResponse.text,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to download the processed PDF
app.get('/download/:filename', (req, res) => {
  const filePath = path.join(__dirname, 'storage/pdfs', req.params.filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).send('File not found');
  }
});

// Endpoint to save a transcript
app.post('/transcript', (req, res) => {
  const { filename, transcript } = req.body;

  if (!filename || !transcript) {
    return res.status(400).json({ error: 'Filename and transcript are required' });
  }

  const transcriptPath = path.join(__dirname, 'storage/transcripts', `${filename}.json`);

  fs.writeFile(transcriptPath, JSON.stringify(transcript), (err) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to save transcript' });
    }

    res.status(200).json({ message: 'Transcript saved successfully' });
  });
});

// Endpoint to get a transcript
app.get('/transcript/:filename', (req, res) => {
  const transcriptPath = path.join(__dirname, 'storage/transcripts', `${req.params.filename}.json`);

  if (fs.existsSync(transcriptPath)) {
    res.sendFile(transcriptPath);
  } else {
    res.status(404).json({ error: 'Transcript not found' });
  }
});

app.get('/api/cues', (req, res) => {
  const state = automerge.save(doc);
  let annotations = doc.annotations.map(convertTagsToList);
  res.json({annotations: annotations});
});


// Start SpeechToLine process
app.post('/stlp/start', async (req, res) => {
  try {
    const response = await startSpeechToLine();
    if (response.success) {
      res.json({ message: 'SpeechToLine process started successfully' });
    } else {
      res.status(500).json({ message: 'Failed to start SpeechToLine process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Stop SpeechToLine process
app.post('/stlp/stop', async (req, res) => {
  try {
    const response = await stopSpeechToLine();
    if (response.success) {
      res.json({ message: 'SpeechToLine process stopped successfully' });
    } else {
      res.status(500).json({ message: 'Failed to stop SpeechToLine process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start Performer Tracker process
app.post('/pt/start', async (req, res) => {
  try {
    const response = await startPerformerTracker();
    if (response.success) {
      res.json({ message: 'Performer Tracker process started successfully' });
    } else {
      res.status(500).json({ message: 'Failed to start Performer Tracker process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Stop Performer Tracker process
app.post('/pt/stop', async (req, res) => {
  try {
    const response = await stopPerformerTracker();
    if (response.success) {
      res.json({ message: 'Performer Tracker process stopped successfully' });
    } else {
      res.status(500).json({ message: 'Failed to stop Performer Tracker process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Status endpoint
app.get('/status', (req, res) => {
  res.json({ status: 'running' });
});

const PORT = process.env.PORT || 4000;
const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

// WebSocket Server for Automerge
const wss = new WebSocket.Server({ server });

function broadcastChanges(changes) {
  const message = JSON.stringify({ changes });
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

wss.on('connection', (ws) => {
  clients.add(ws);

  ws.on('close', () => {
    clients.delete(ws);
  });

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      if (data && data.changes) {
        let newDoc = automerge.clone(doc);
        newDoc = automerge.change(newDoc, d => {
          if (!d.annotations) d.annotations = [];
          data.changes.forEach(change => {
            change.annotation = convertTagsToList(change.annotation);
            switch (change.type) {
              case 'add':
                d.annotations.push(change.annotation);
                break;
              case 'update':
                const index = d.annotations.findIndex(a => a.id === change.annotation.id);
                if (index !== -1 && change.timestamp >= (d.annotations[index].timestamp || 0)) {
                  Object.keys(change.annotation).forEach(key => {
                    if (typeof change.annotation[key] === 'object' && change.annotation[key] !== null) {
                      d.annotations[index][key] = {
                        ...d.annotations[index][key],
                        ...change.annotation[key]
                      };
                    } else {
                      d.annotations[index][key] = change.annotation[key];
                    }
                  });
                  d.annotations[index].timestamp = change.timestamp;
                }
                break;
              case 'delete':
                const deleteIndex = d.annotations.findIndex(a => a.id === change.annotation.id);
                if (deleteIndex !== -1) {
                  d.annotations.splice(deleteIndex, 1);
                }
                break;
            }
          });
        });

        doc = automerge.merge(doc, newDoc);
        saveCues();
        broadcastChanges(data.changes);
        ws.send(JSON.stringify({ ack: data.changes.map(change => change.id) }));
      }
    } catch (error) {
      console.error('Failed to process message:', error);
    }
  });

  const state = automerge.save(doc);
  // ws.send(JSON.stringify({ annotations: doc.annotations }));
});


function convertTagsToList(annotation) {
  if (annotation.tags && typeof annotation.tags === 'object' && !Array.isArray(annotation.tags)) {
    annotation.tags = Object.values(annotation.tags);
  }
  return annotation;
}
