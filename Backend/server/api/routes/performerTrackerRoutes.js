/**
 * @file routes/performerTrackerRoutes.js
 * @description Routes for starting and stopping the performer tracker service using the performerTrackerController.
 * @version 1.0.0
 * @version 1.0.0
 * @date 06/06/2024
 */

const express = require("express");
const performerTrackerController = require("../controllers/performerTrackerController");

const router = express.Router();

router.post(
  "/performer-tracker/start",
  performerTrackerController.startPerformerTracker
);
router.post(
  "/performer-tracker/stop",
  performerTrackerController.stopPerformerTracker
);

module.exports = router;
