/*
 * Author: Jack Beaumont
 * Date: 06/06/2024
 *
 * Description:
 * This file contains the ApiProvider class, which provides methods to upload
 * PDF files, upload PDF file bytes, fetch PDFs, and send extracted text.
 */

import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';

class ApiProvider {
  final String baseUrl;
  final Logger _logger = Logger();

  ApiProvider(this.baseUrl);

  /// Uploads a PDF file to the server.
  /// 
  /// [filePath] is the local path of the PDF file to be uploaded.
  /// [marginSide] specifies the margin side.
  /// 
  /// Returns a [Future] containing a map of the server response.
  Future<Map<String, dynamic>> uploadPDF(String filePath, String marginSide) async {
    _logger.i('Uploading PDF from file path: $filePath');
    
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/script/upload'));
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    request.fields['marginSide'] = marginSide;

    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    _logger.i('Upload PDF response: $responseData');
    return json.decode(responseData);
  }

  /// Uploads PDF bytes to the server.
  ///
  /// [fileBytes] contains the bytes of the PDF file to be uploaded.
  /// [marginSide] specifies the margin side.
  ///
  /// Returns a [Future] containing a map of the server response.
  /// Throws an [Exception] if the upload fails.
  Future<Map<String, dynamic>> uploadPDFBytes(Uint8List fileBytes, String marginSide) async {
    _logger.i('Uploading PDF from bytes');
    
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/script/upload'));
    request.files.add(http.MultipartFile.fromBytes('file', fileBytes, filename: 'upload.pdf'));
    request.fields['marginSide'] = marginSide;

    var response = await request.send();
    if (response.statusCode == 201) {
      var responseData = await response.stream.bytesToString();
      _logger.i('Upload PDF bytes response: $responseData');
      return json.decode(responseData);
    } else {
      _logger.e('Failed to upload PDF, status code: ${response.statusCode}');
      throw Exception('Failed to upload PDF');
    }
  }

  /// Fetches a PDF from the server.
  ///
  /// [filename] is the name of the PDF file to be fetched.
  ///
  /// Returns a [Future] containing a map of the server response.
  Future<Map<String, dynamic>> fetchPDF(String filename) async {
    _logger.i('Fetching PDF with filename: $filename');
    
    var response = await http.get(Uri.parse('$baseUrl/api/script/download/$filename'));
    _logger.i('Fetch PDF response: ${response.body}');
    return json.decode(response.body);
  }

  /// Sends extracted text to the server.
  ///
  /// [filename] is the name of the file being sent.
  /// [ocrText] contains the extracted text data.
  ///
  /// Returns a [Future] containing the HTTP response.
  Future<http.Response> sendExtractedText(String filename, Map<String, dynamic> ocrText) async {
    _logger.i('Sending extracted text for filename: $filename');
    
    final response = await http.post(
      Uri.parse('$baseUrl/api/transcripts'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'filename': filename, 'transcript': ocrText}),
    );
    _logger.i('Send extracted text response: ${response.body}');
    return response;
  }
}
