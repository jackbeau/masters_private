/**
 * @file routes/transcriptRoutes.js
 * @description Routes for handling transcript-related requests.
 * @author Jack Beaumont
 * @date 06/06/2024
 */

const express = require('express');
const transcriptController = require('../controllers/transcriptController');

const router = express.Router();

router.post('/transcripts', transcriptController.saveTranscript);
router.get('/transcript/:filename', transcriptController.getTranscript);

module.exports = router;
