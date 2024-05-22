const express = require('express');
const cors = require('cors');
const { createHandler } = require('graphql-http/lib/use/express');
const { buildSchema } = require('graphql');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const typeDefs = require('./graphql/typeDefs');
const resolvers = require('./graphql/resolvers');
const { addMargin, performOCR } = require('./grpc/client/client');

// Construct a schema, using GraphQL schema language
const schema = buildSchema(typeDefs);

// The root provides a resolver function for each API endpoint
const root = resolvers;

const app = express();
app.use(cors());
app.use(express.json()); // Add this line to parse JSON bodies

// Set up multer for file uploads
const upload = multer({ dest: 'server/storage/pdfs/' });

// Create and use the GraphQL handler.
app.all(
  '/graphql',
  createHandler({
    schema: schema,
    rootValue: root,
  })
);

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

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}/graphql`);
});
