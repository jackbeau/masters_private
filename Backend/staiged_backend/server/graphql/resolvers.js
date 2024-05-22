const path = require('path');
const { addMargin, performOCR } = require('../grpc/client/client');

const resolvers = {
  hello: () => 'Hello world!',
  async uploadPDF({ filename, marginSide }) {
    const filePath = path.join(__dirname, '../storage/pdfs', filename);

    // Add margin
    const addMarginResponse = await addMargin(filePath, marginSide);

    // Perform OCR
    const ocrResponse = await performOCR(addMarginResponse.file_path);

    return {
      filename,
      filepath: addMarginResponse.file_path,
      ocrText: ocrResponse.text,
    };
  },
};

module.exports = resolvers;
