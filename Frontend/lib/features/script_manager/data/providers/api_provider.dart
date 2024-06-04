import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiProvider {
  final String baseUrl;

  ApiProvider(this.baseUrl);

  Future<Map<String, dynamic>> uploadPDF(String filePath, String marginSide) async {
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/script/upload'));
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    request.fields['marginSide'] = marginSide;

    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    return json.decode(responseData);
  }

  Future<Map<String, dynamic>> uploadPDFBytes(Uint8List fileBytes, String marginSide) async {
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/script/upload'));
    request.files.add(http.MultipartFile.fromBytes('file', fileBytes, filename: 'upload.pdf'));
    request.fields['marginSide'] = marginSide;

    var response = await request.send();
    if (response.statusCode == 201) {
      var responseData = await response.stream.bytesToString();
      return json.decode(responseData);
    } else {
      throw Exception('Failed to upload PDF');
    }
  }

  Future<Map<String, dynamic>> fetchPDF(String filename) async {
    var response = await http.get(Uri.parse('$baseUrl/api/script/download/$filename'));
    return json.decode(response.body);
  }

  Future<http.Response> sendExtractedText(String filename, Map<String, dynamic> ocrText) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/transcripts'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'filename': "output_extracted_data", 'transcript': ocrText}), // Fix the body structure
    );
    return response;
  }
}
