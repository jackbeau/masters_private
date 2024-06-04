class PDFModel {
  final String filename;
  final String filepath;

  PDFModel({required this.filename, required this.filepath});

  factory PDFModel.fromJson(Map<String, dynamic> json) {
    return PDFModel(
      filename: json['filename'],
      filepath: json['filepath'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'filename': filename,
      'filepath': filepath,
    };
  }
}
