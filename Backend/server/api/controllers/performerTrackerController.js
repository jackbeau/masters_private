/**
 * @file controllers/performerTrackerController.js
 * @description Controller for handling the start and stop operations of the Performer Tracker process using gRPC client.
 * @version 1.0.0
 * @date 06/06/2024
 */

const {
  startPerformerTracker,
  stopPerformerTracker,
} = require("../../grpc/client/client");

/**
 * Starts the Performer Tracker process.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @returns {Object} Response with a success message or an error message.
 */
exports.startPerformerTracker = async (req, res) => {
  try {
    const response = await startPerformerTracker();
    if (response.success) {
      res
        .status(200)
        .json({ message: "Performer Tracker process started successfully" });
    } else {
      res
        .status(500)
        .json({ message: "Failed to start Performer Tracker process" });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

/**
 * Stops the Performer Tracker process.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @returns {Object} Response with a success message or an error message.
 */
exports.stopPerformerTracker = async (req, res) => {
  try {
    const response = await stopPerformerTracker();
    if (response.success) {
      res
        .status(200)
        .json({ message: "Performer Tracker process stopped successfully" });
    } else {
      res
        .status(500)
        .json({ message: "Failed to stop Performer Tracker process" });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
