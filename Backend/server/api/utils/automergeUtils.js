const automerge = require('@automerge/automerge');
const fs = require('fs');
const path = require('path');

const cuesFilePath = path.join(__dirname, '../storage/cues', 'cues.json');

let doc = automerge.init();

if (fs.existsSync(cuesFilePath)) {
  const savedState = fs.readFileSync(cuesFilePath);
  doc = automerge.load(savedState);
} else {
  doc = automerge.change(doc, d => {
    d.annotations = [];
  });
  saveCues();
}

function saveCues() {
  try {
    fs.mkdirSync(path.dirname(cuesFilePath), { recursive: true });
    const state = automerge.save(doc);
    fs.writeFileSync(cuesFilePath, state);
  } catch (error) {
    console.error('Failed to save cues:', error);
  }
}

function convertTagsToList(annotation) {
  if (annotation.tags && typeof annotation.tags === 'object' && !Array.isArray(annotation.tags)) {
    annotation.tags = Object.values(annotation.tags);
  }
  return annotation;
}

module.exports = {
  doc,
  saveCues,
  convertTagsToList,
};
