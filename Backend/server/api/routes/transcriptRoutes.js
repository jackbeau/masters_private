const express = require('express');
const transcriptController = require('../controllers/transcriptController');

const router = express.Router();

router.post('/transcripts', transcriptController.saveTranscript);
router.get('/transcript/:filename', transcriptController.getTranscript);

module.exports = router;
