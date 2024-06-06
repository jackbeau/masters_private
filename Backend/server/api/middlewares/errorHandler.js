/**
 * @file middleware/errorHandler.js
 * @description Middleware for handling errors in the application.
 * @version 1.0.0
 * @date 06/06/2024
 */

/**
 * Error handling middleware for Express applications.
 * @param {Object} err - The error object.
 * @param {Object} req - The Express request object.
 * @param {Object} res - The Express response object.
 * @param {Function} next - The next middleware function in the stack.
 */
module.exports = function errorHandler(err, req, res, next) {
  // Log the error stack for debugging purposes
  console.error(err.stack);

  // Send a 500 Internal Server Error response with a generic error message
  res.status(500).json({ error: "An unexpected error occurred" });
};
