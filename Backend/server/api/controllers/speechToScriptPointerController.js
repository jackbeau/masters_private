const { startSpeechToScriptPointer, stopSpeechToScriptPointer } = require('../../grpc/client/client');

exports.startSpeechToScriptPointer = async (req, res) => {
  try {
    const response = await startSpeechToScriptPointer();
    if (response.success) {
      res.status(200).json({ message: 'SpeechToScriptPointer process started successfully' });
    } else {
      res.status(500).json({ message: 'Failed to start SpeechToScriptPointer process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.stopSpeechToScriptPointer = async (req, res) => {
  try {
    const response = await stopSpeechToScriptPointer();
    if (response.success) {
      res.status(200).json({ message: 'SpeechToScriptPointer process stopped successfully' });
    } else {
      res.status(500).json({ message: 'Failed to stop SpeechToScriptPointer process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
