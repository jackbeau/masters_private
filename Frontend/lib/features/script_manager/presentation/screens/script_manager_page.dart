/// ScriptManager.dart
/// Author: Jack Beaumont
/// Date: 06/06/2024
/// 
/// This file manages the script for handling PDF file picking and uploading functionalities.
library;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:file_picker/file_picker.dart';
import 'package:logging/logging.dart'; // Added for logging
import '../../data/providers/api_provider.dart';
import '../../data/repositories/pdf_repository.dart';
import '../../data/interfaces/pdf_repository_interface.dart';
import '../../domain/bloc/pdf_bloc.dart';
import '../widgets/pdf_viewer.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

// Initialize the logger
final Logger _logger = Logger('ScriptManager');

class ScriptManager extends StatelessWidget {
  const ScriptManager({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<ApiProvider>(
          create: (context) => ApiProvider('http://localhost:4000'),
        ),
        RepositoryProvider<PDFRepositoryInterface>(
          create: (context) => PDFRepository(context.read<ApiProvider>()),
        ),
      ],
      child: BlocProvider<PDFBloc>(
        create: (context) => PDFBloc(context.read<PDFRepositoryInterface>()),
        child: const PDFForm(),
      ),
    );
  }
}

class PDFForm extends StatefulWidget {
  const PDFForm({super.key});

  @override
  PDFFormState createState() => PDFFormState();
}

class PDFFormState extends State<PDFForm> {
  String? fileName;
  dynamic filePath;
  String marginSide = 'none';

  /// Picks a PDF file using the file picker.
  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );
    if (result != null) {
      setState(() {
        fileName = result.files.single.name;
        filePath = kIsWeb ? result.files.single.bytes : result.files.single.path;
      });
      _logger.info('File picked: $fileName');
    } else {
      _logger.warning('File picking cancelled');
    }
  }

  /// Uploads the picked PDF file using the appropriate method based on the platform.
  void _uploadFile(BuildContext context) {
    if (filePath != null) {
      if (kIsWeb) {
        BlocProvider.of<PDFBloc>(context).add(UploadPDFBytes(filePath, marginSide));
      } else {
        BlocProvider.of<PDFBloc>(context).add(UploadPDF(filePath, marginSide));
      }
      _logger.info('File upload initiated: $fileName with margin $marginSide');
    } else {
      _logger.warning('No file to upload');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            elevation: 2,
            margin: const EdgeInsets.only(bottom: 16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ElevatedButton.icon(
                    onPressed: _pickFile,
                    icon: const Icon(Icons.attach_file),
                    label: const Text('Pick PDF File'),
                  ),
                  if (fileName != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      'Selected file: $fileName',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                    ),
                  ],
                ],
              ),
            ),
          ),
          DropdownButtonFormField<String>(
            value: marginSide,
            decoration: const InputDecoration(
              labelText: 'Margin Side',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'none', child: Text('None')),
              DropdownMenuItem(value: 'left', child: Text('Left')),
              DropdownMenuItem(value: 'right', child: Text('Right')),
            ],
            onChanged: (value) {
              setState(() {
                marginSide = value!;
              });
              _logger.info('Margin side changed to: $marginSide');
            },
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => _uploadFile(context),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              textStyle: const TextStyle(fontSize: 16),
            ),
            child: const Text('Upload PDF'),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: BlocBuilder<PDFBloc, PDFState>(
              builder: (context, state) {
                if (state is PDFLoading) {
                  return const Center(child: CircularProgressIndicator());
                } else if (state is PDFSuccess) {
                  return PDFViewer(pdf: state.pdf);
                } else if (state is PDFError) {
                  return Text('Error: ${state.message}', style: const TextStyle(color: Colors.red));
                }
                return Container();
              },
            ),
          ),
        ],
      ),
    );
  }
}
