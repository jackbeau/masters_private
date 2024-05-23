const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { addMargin, performOCR } = require('./grpc/client/client');

const app = express();
app.use(cors());
app.use(express.json({ limit: '100mb' }));

// File path for storing cues
const cuesFilePath = path.join(__dirname, 'storage', 'cues.json');

// Helper functions
const loadCues = () => {
  if (!fs.existsSync(cuesFilePath)) {
    return [];
  }
  const cuesData = fs.readFileSync(cuesFilePath);
  return JSON.parse(cuesData);
};

const saveCues = (cues) => {
  fs.writeFileSync(cuesFilePath, JSON.stringify(cues, null, 2));
};

// Set up multer for file uploads
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

// CRUD endpoints for cues

// Get all cues
app.get('/api/cues', (req, res) => {
  const cues = loadCues();
  res.json(cues);
});

// Get a specific cue by ID
app.get('/api/cues/:id', (req, res) => {
  const cues = loadCues();
  const cue = cues.find(c => c.id === req.params.id);
  if (cue) {
    res.json(cue);
  } else {
    res.status(404).json({ error: 'Cue not found' });
  }
});

// Add a new cue
app.post('/api/cues', (req, res) => {
  const cues = loadCues();
  const newCue = req.body;
  newCue.id = newCue.id || String(Date.now()); // Generate an ID if not provided
  cues.push(newCue);
  saveCues(cues);
  res.status(201).json(newCue);
});

// Update an existing cue
app.put('/api/cues/:id', (req, res) => {
  const cues = loadCues();
  const index = cues.findIndex(c => c.id === req.params.id);
  if (index !== -1) {
    cues[index] = { ...cues[index], ...req.body };
    saveCues(cues);
    res.json(cues[index]);
  } else {
    res.status(404).json({ error: 'Cue not found' });
  }
});

// Delete a cue
app.delete('/api/cues/:id', (req, res) => {
  const cues = loadCues();
  const index = cues.findIndex(c => c.id === req.params.id);
  if (index !== -1) {
    const deletedCue = cues.splice(index, 1);
    saveCues(cues);
    res.json(deletedCue);
  } else {
    res.status(404).json({ error: 'Cue not found' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
