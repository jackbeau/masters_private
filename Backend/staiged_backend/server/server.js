const express = require('express');
const { createHandler } = require('graphql-http/lib/use/express');
const { buildSchema } = require('graphql');
const multer = require('multer');
const path = require('path');
const typeDefs = require('./graphql/typeDefs');
const resolvers = require('./graphql/resolvers');
const { addMargin, performOCR } = require('./grpc/client/client'); // Correct import statement

// Construct a schema, using GraphQL schema language
const schema = buildSchema(typeDefs);

// The root provides a resolver function for each API endpoint
const root = resolvers;

const app = express();

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

    // Return the modified PDF and OCR text
    res.json({
      filename: file.filename,
      filepath: addMarginResponse.file_path,
      ocrText: ocrResponse.text,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}/graphql`);
});
