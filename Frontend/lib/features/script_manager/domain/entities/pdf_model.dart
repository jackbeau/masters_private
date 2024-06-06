// Author: Jack Beaumont
// Date: 06/06/2024

import 'package:logger/logger.dart';

// Initialize a logger instance
final Logger logger = Logger();

/// A model class for representing a PDF file with its filename and filepath.
class PDFModel {
  final String filename;
  final String filepath;

  /// Creates an instance of [PDFModel].
  /// 
  /// [filename] is the name of the PDF file.
  /// [filepath] is the path where the PDF file is stored.
  PDFModel({required this.filename, required this.filepath});

  /// Factory constructor to create a [PDFModel] instance from a JSON object.
  /// 
  /// [json] is a map representing the JSON object.
  /// Returns a [PDFModel] instance.
  factory PDFModel.fromJson(Map<String, dynamic> json) {
    logger.d('Creating PDFModel from JSON: $json');
    return PDFModel(
      filename: json['filename'],
      filepath: json['filepath'],
    );
  }

  /// Converts the [PDFModel] instance to a JSON object.
  /// 
  /// Returns a map representing the JSON object.
  Map<String, dynamic> toJson() {
    final json = {
      'filename': filename,
      'filepath': filepath,
    };
    logger.d('Converting PDFModel to JSON: $json');
    return json;
  }
}
