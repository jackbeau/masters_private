class PDFModel {
  final String filename;
  final String filepath;
  final String ocrText;

  PDFModel({required this.filename, required this.filepath, required this.ocrText});

  factory PDFModel.fromJson(Map<String, dynamic> json) {
    return PDFModel(
      filename: json['filename'],
      filepath: json['filepath'],
      ocrText: json['ocrText'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'filename': filename,
      'filepath': filepath,
      'ocrText': ocrText,
    };
  }
}
