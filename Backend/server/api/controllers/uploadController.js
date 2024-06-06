/**
 * @file controllers/uploadController.js
 * @description Controller for handling PDF upload and download operations, including adding margins and performing OCR using gRPC client.
 * @version 1.0.0
 * @date 06/06/2024
 */

const path = require("path");
const fs = require("fs");
const { addMargin, performOCR } = require("../../grpc/client/client");

/**
 * Uploads a PDF file, optionally performs OCR, adds a margin, and returns the file URL.
 * @param {Object} req - Express request object, with file data and optional OCR flag.
 * @param {Object} res - Express response object.
 * @returns {Object} Response with the filename and file URL.
 */
exports.uploadPDF = async (req, res) => {
  const file = req.file;
  const marginSide = req.body.marginSide;
  const ocr = req.body.ocr;

  if (!file || !marginSide) {
    return res.status(400).json({ error: "File and marginSide are required" });
  }

  try {
    let addMarginResponse;
    if (ocr) {
      const ocrResponse = await performOCR(file.path);
      addMarginResponse = await addMargin(ocrResponse.file_path, marginSide);
    } else {
      addMarginResponse = await addMargin(file.path, marginSide);
    }
    const filename = path.basename(addMarginResponse.file_path);
    const fullUrl = `${req.protocol}://${req.get(
      "host"
    )}/api/script/download/${filename}`;

    res.status(201).json({
      filename: file.filename,
      filepath: fullUrl,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  } finally {
    fs.unlink(file.path, (err) => {
      if (err) console.error("Failed to delete file:", err);
    });
  }
};

/**
 * Downloads a PDF file by filename.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @returns {Object} The PDF file as a download response or a 404 error if the file is not found.
 */
exports.downloadPDF = (req, res) => {
  const filePath = path.join(
    __dirname,
    "../../storage/pdfs",
    req.params.filename
  );
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).send("File not found");
  }
};
