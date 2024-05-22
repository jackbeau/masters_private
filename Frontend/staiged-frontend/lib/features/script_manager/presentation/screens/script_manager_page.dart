import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:file_picker/file_picker.dart';
import '../../data/providers/api_provider.dart';
import '../../data/repositories/pdf_repository.dart';
import '../../data/interfaces/pdf_repository_interface.dart';
import '../../domain/bloc/pdf_bloc.dart';
import '../widgets/pdf_viewer.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

class ScriptManager extends StatelessWidget {
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
        child: PDFForm(),
      ),
    );
  }
}

class PDFForm extends StatefulWidget {
  @override
  _PDFFormState createState() => _PDFFormState();
}

class _PDFFormState extends State<PDFForm> {
  String? fileName;
  dynamic filePath;
  String marginSide = 'none';

  void _pickFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['pdf']);
    if (result != null) {
      setState(() {
        fileName = result.files.single.name;
        if (kIsWeb) {
          filePath = result.files.single.bytes;
        } else {
          filePath = result.files.single.path;
        }
      });
    }
  }

  void _uploadFile(BuildContext context) {
    if (filePath != null) {
      if (kIsWeb) {
        BlocProvider.of<PDFBloc>(context).add(UploadPDFBytes(filePath, marginSide));
      } else {
        BlocProvider.of<PDFBloc>(context).add(UploadPDF(filePath, marginSide));
      }
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
                    icon: Icon(Icons.attach_file),
                    label: Text('Pick PDF File'),
                  ),
                  if (fileName != null) ...[
                    SizedBox(height: 10),
                    Text(
                      'Selected file: $fileName',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                    ),
                  ],
                ],
              ),
            ),
          ),
          DropdownButtonFormField<String>(
            value: marginSide,
            decoration: InputDecoration(
              labelText: 'Margin Side',
              border: OutlineInputBorder(),
            ),
            items: [
              DropdownMenuItem(child: Text('None'), value: 'none'),
              DropdownMenuItem(child: Text('Left'), value: 'left'),
              DropdownMenuItem(child: Text('Right'), value: 'right'),
            ],
            onChanged: (value) {
              setState(() {
                marginSide = value!;
              });
            },
          ),
          SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => _uploadFile(context),
            child: Text('Upload PDF'),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              textStyle: TextStyle(fontSize: 16),
            ),
          ),
          SizedBox(height: 20),
          Expanded(
            child: BlocBuilder<PDFBloc, PDFState>(
              builder: (context, state) {
                if (state is PDFLoading) {
                  return Center(child: CircularProgressIndicator());
                } else if (state is PDFSuccess) {
                  return PDFViewer(pdf: state.pdf);
                } else if (state is PDFError) {
                  return Text('Error: ${state.message}', style: TextStyle(color: Colors.red));
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
