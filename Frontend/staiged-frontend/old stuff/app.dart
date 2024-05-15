import 'package:flutter/material.dart';
// import 'package:flutter_gen/gen_l10n/app_localizations.dart';
// import 'package:flutter_localizations/flutter_localizations.dart';

// import 'sample_feature/sample_item_details_view.dart';
// import 'sample_feature/sample_item_list_view.dart';
// import '../lib/features/settings/settings_controller.dart';
// import '../lib/features/settings/settings_view.dart';

// import 'package:flutter/material.dart';
import 'package:pdfx/pdfx.dart';

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late PdfControllerPinch pdfControllerPinch;

  int totalPageCount = 0, currentPage = 1;

  @override
  void initState() {
    super.initState();
    pdfControllerPinch = PdfControllerPinch(
        document: PdfDocument.openAsset('assets/input.pdf'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "PDF Viewer",
          style: TextStyle(
            color: Colors.white,
          ),
        ),
        backgroundColor: Colors.red,
      ),
      body: _buildUI(),
    );
  }

  Widget _buildUI() {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text("Total Pages: ${totalPageCount}"),
            IconButton(
              onPressed: () {
                pdfControllerPinch.previousPage(
                  duration: Duration(
                    milliseconds: 500,
                  ),
                  curve: Curves.linear,
                );
              },
              icon: Icon(
                Icons.arrow_back,
              ),
            ),
            Text("Current Page: ${currentPage}"),
            IconButton(
              onPressed: () {
                pdfControllerPinch.nextPage(
                  duration: Duration(
                    milliseconds: 500,
                  ),
                  curve: Curves.linear,
                );
              },
              icon: Icon(
                Icons.arrow_forward,
              ),
            ),
          ],
        ),
        _pdfView(),
      ],
    );
  }

  Widget _pdfView() {
    return Expanded(
      child: PdfViewPinch(
        scrollDirection: Axis.vertical,
        controller: pdfControllerPinch,
        onDocumentLoaded: (doc) {
          setState(() {
            totalPageCount = doc.pagesCount;
          });
        },
        onPageChanged: (page) {
          setState(() {
            currentPage = page;
          });
        },
      ),
    );
  }
}



// /// The Widget that configures your application.
// class MyApp extends StatelessWidget {
//   const MyApp({
//     super.key,
//     required this.settingsController,
//   });

//   final SettingsController settingsController;

//   @override
//   Widget build(BuildContext context) {
//     // Glue the SettingsController to the MaterialApp.
//     //
//     // The ListenableBuilder Widget listens to the SettingsController for changes.
//     // Whenever the user updates their settings, the MaterialApp is rebuilt.
//     return ListenableBuilder(
//       listenable: settingsController,
//       builder: (BuildContext context, Widget? child) {
//         return MaterialApp(
//           // Providing a restorationScopeId allows the Navigator built by the
//           // MaterialApp to restore the navigation stack when a user leaves and
//           // returns to the app after it has been killed while running in the
//           // background.
//           restorationScopeId: 'app',

//           // Provide the generated AppLocalizations to the MaterialApp. This
//           // allows descendant Widgets to display the correct translations
//           // depending on the user's locale.
//           localizationsDelegates: const [
//             AppLocalizations.delegate,
//             GlobalMaterialLocalizations.delegate,
//             GlobalWidgetsLocalizations.delegate,
//             GlobalCupertinoLocalizations.delegate,
//           ],
//           supportedLocales: const [
//             Locale('en', ''), // English, no country code
//           ],

//           // Use AppLocalizations to configure the correct application title
//           // depending on the user's locale.
//           //
//           // The appTitle is defined in .arb files found in the localization
//           // directory.
//           onGenerateTitle: (BuildContext context) =>
//               AppLocalizations.of(context)!.appTitle,

//           // Define a light and dark color theme. Then, read the user's
//           // preferred ThemeMode (light, dark, or system default) from the
//           // SettingsController to display the correct theme.
//           theme: ThemeData(),
//           darkTheme: ThemeData.dark(),
//           themeMode: settingsController.themeMode,

//           // Define a function to handle named routes in order to support
//           // Flutter web url navigation and deep linking.
//           onGenerateRoute: (RouteSettings routeSettings) {
//             return MaterialPageRoute<void>(
//               settings: routeSettings,
//               builder: (BuildContext context) {
//                 switch (routeSettings.name) {
//                   case SettingsView.routeName:
//                     return SettingsView(controller: settingsController);
//                   case SampleItemDetailsView.routeName:
//                     return const SampleItemDetailsView();
//                   case SampleItemListView.routeName:
//                   default:
//                     return const SampleItemListView();
//                 }
//               },
//             );
//           },
//         );
//       },
//     );
//   }
// }
