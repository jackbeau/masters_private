const path = require('path');
const fs = require('fs');

exports.saveTranscript = (req, res) => {
  const { filename, transcript } = req.body;

  if (!filename || !transcript) {
    return res.status(400).json({ error: 'Filename and transcript are required' });
  }

  const transcriptPath = path.join(__dirname, '../storage/transcripts', `${filename}.json`);

  fs.writeFile(transcriptPath, JSON.stringify(transcript), (err) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to save transcript' });
    }

    res.status(201).json({ message: 'Transcript saved successfully' });
  });
};

exports.getTranscript = (req, res) => {
  const transcriptPath = path.join(__dirname, '../storage/transcripts', `${req.params.filename}.json`);

  if (fs.existsSync(transcriptPath)) {
    res.sendFile(transcriptPath);
  } else {
    res.status(404).json({ error: 'Transcript not found' });
  }
};
