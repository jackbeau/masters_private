const express = require('express');
const performerTrackerController = require('../controllers/performerTrackerController');

const router = express.Router();

router.post('/performer-tracker/start', performerTrackerController.startPerformerTracker);
router.post('/performer-tracker/stop', performerTrackerController.stopPerformerTracker);

module.exports = router;
