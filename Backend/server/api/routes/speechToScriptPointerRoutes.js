const express = require('express');
const speechToScriptPointerController = require('../controllers/speechToScriptPointerController');

const router = express.Router();

router.post('/speech-to-script-pointer/start', speechToScriptPointerController.startSpeechToScriptPointer);
router.post('/speech-to-script-pointer/stop', speechToScriptPointerController.stopSpeechToScriptPointer);

module.exports = router;
