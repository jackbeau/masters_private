/**
 * @file controllers/speechToScriptPointerController.js
 * @description Controller for handling the start and stop operations of the SpeechToScriptPointer process using gRPC client.
 * @version 1.0.0
 * @date 06/06/2024
 */

const {
  startSpeechToScriptPointer,
  stopSpeechToScriptPointer,
} = require("../../grpc/client/client");

/**
 * Starts the SpeechToScriptPointer process.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @returns {Object} Response with a success message or an error message.
 */
exports.startSpeechToScriptPointer = async (req, res) => {
  try {
    const response = await startSpeechToScriptPointer();
    if (response.success) {
      res
        .status(200)
        .json({
          message: "SpeechToScriptPointer process started successfully",
        });
    } else {
      res
        .status(500)
        .json({ message: "Failed to start SpeechToScriptPointer process" });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

/**
 * Stops the SpeechToScriptPointer process.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @returns {Object} Response with a success message or an error message.
 */
exports.stopSpeechToScriptPointer = async (req, res) => {
  try {
    const response = await stopSpeechToScriptPointer();
    if (response.success) {
      res
        .status(200)
        .json({
          message: "SpeechToScriptPointer process stopped successfully",
        });
    } else {
      res
        .status(500)
        .json({ message: "Failed to stop SpeechToScriptPointer process" });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
