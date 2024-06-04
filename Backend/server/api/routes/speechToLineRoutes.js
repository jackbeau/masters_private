const express = require('express');
const speechToLineController = require('../controllers/speechToLineController');

const router = express.Router();

router.post('/speech-to-line/start', speechToLineController.startSpeechToLine);
router.post('/speech-to-line/stop', speechToLineController.stopSpeechToLine);

module.exports = router;
