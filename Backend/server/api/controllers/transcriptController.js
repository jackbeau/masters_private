/**
 * @file controllers/transcriptController.js
 * @description Controller for handling transcript saving and retrieval operations.
 * @version 1.0.0
 * @date 06/06/2024
 */

const path = require("path");
const fs = require("fs");

/**
 * Saves a transcript to a file.
 * @param {Object} req - Express request object containing the filename and transcript in the body.
 * @param {Object} res - Express response object.
 * @returns {Object} Response with a success message or an error message.
 */
exports.saveTranscript = (req, res) => {
  const { filename, transcript } = req.body;

  if (!filename || !transcript) {
    return res
      .status(400)
      .json({ error: "Filename and transcript are required" });
  }

  const transcriptPath = path.join(
    __dirname,
    "../../storage/transcripts",
    `${filename}.json`
  );

  fs.writeFile(transcriptPath, JSON.stringify(transcript), (err) => {
    if (err) {
      return res.status(500).json({ error: "Failed to save transcript" });
    }

    res.status(201).json({ message: "Transcript saved successfully" });
  });
};

/**
 * Retrieves a transcript file by filename.
 * @param {Object} req - Express request object containing the filename in the URL parameters.
 * @param {Object} res - Express response object.
 * @returns {Object} The transcript file or an error message if not found.
 */
exports.getTranscript = (req, res) => {
  const transcriptPath = path.join(
    __dirname,
    "../../storage/transcripts",
    `${req.params.filename}.json`
  );

  if (fs.existsSync(transcriptPath)) {
    res.sendFile(transcriptPath);
  } else {
    res.status(404).json({ error: "Transcript not found" });
  }
};
