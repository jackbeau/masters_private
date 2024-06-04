const path = require('path');
const fs = require('fs');
const { addMargin, performOCR } = require('../../grpc/client/client');

exports.uploadPDF = async (req, res) => {
  const file = req.file;
  const marginSide = req.body.marginSide;

  if (!file || !marginSide) {
    return res.status(400).json({ error: 'File and marginSide are required' });
  }

  try {
    const addMarginResponse = await addMargin(file.path, marginSide);
    const ocrResponse = await performOCR(addMarginResponse.file_path);
    const filename = path.basename(addMarginResponse.file_path);
    const fullUrl = `${req.protocol}://${req.get('host')}/download/${filename}`;

    res.status(201).json({
      filename: file.filename,
      filepath: fullUrl,
      ocrText: ocrResponse.text,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  } finally {
    fs.unlink(file.path, err => {
      if (err) console.error('Failed to delete file:', err);
    });
  }
};

exports.downloadPDF = (req, res) => {
  const filePath = path.join(__dirname, '../storage/pdfs', req.params.filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).send('File not found');
  }
};
