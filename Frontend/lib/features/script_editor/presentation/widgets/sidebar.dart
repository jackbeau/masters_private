import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:stage_assistant/features/script_editor/data/repositories/performer_tracker_repository.dart';
import '../../domain/bloc/sidebar_bloc.dart';
import '../../data/repositories/speech_repository.dart';

class Sidebar extends StatelessWidget {
  const Sidebar({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider<SidebarBloc>(
      create: (context) => SidebarBloc(
        RepositoryProvider.of<SpeechRepository>(context),
        RepositoryProvider.of<PerformerTrackerRepository>(context),
      )..add(LoadActs()),
      child: BlocBuilder<SidebarBloc, SidebarState>(
        builder: (context, state) {
          if (state is SidebarLoaded) {
            return Container(
              width: 200,
              color: Theme.of(context).colorScheme.background,
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Column(
                      children: const [
                        Text('House Open', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                        Divider(color: Colors.grey),
                        Text('Running Time', style: TextStyle(color: Colors.grey, fontSize: 16)),
                        Text('00:17:27', style: TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text('Act Up', style: TextStyle(color: Colors.grey, fontSize: 14)),
                          SizedBox(height: 4), // Adding spacing to bring numbers closer
                          Text('00:17:27', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Local Time', style: TextStyle(color: Colors.grey, fontSize: 14)),
                          const SizedBox(height: 4), // Adding spacing to bring numbers closer
                          Text(state.currentTime, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Text(
                    "Speech-to-script pointer",
                    textAlign: TextAlign.left,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onBackground),
                  ),
                  Wrap(
                    spacing: 8.0, // Add spacing between buttons
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          context.read<SidebarBloc>().add(StartSpeechToScriptPointer());
                        },
                        child: const Text('Start'),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          context.read<SidebarBloc>().add(StopSpeechToScriptPointer());
                        },
                        child: const Text('Stop'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Text(
                    "Performer tracker",
                    textAlign: TextAlign.left,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onBackground),
                  ),
                  Wrap(
                    spacing: 8.0, // Add spacing between buttons
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          context.read<SidebarBloc>().add(StartPerformerTracker());
                        },
                        child: const Text('Start'),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          context.read<SidebarBloc>().add(StopPerformerTracker());
                        },
                        child: const Text('Stop'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  if (state.message.isNotEmpty)
                    Text(
                      state.message,
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  Expanded(
                    child: ListView.builder(
                      itemCount: state.acts.length,
                      itemBuilder: (context, index) {
                        return ExpansionTile(
                          title: Text(state.acts[index].title, style: const TextStyle(color: Colors.white)),
                          children: List<Widget>.from(state.acts[index].scenes.map((scene) =>
                            ListTile(
                              title: Text(scene, style: TextStyle(color: Colors.grey[300])),
                              onTap: () {
                                // Handle scene selection
                                // debugPrint('Selected $scene');
                              },
                            ),
                          )),
                        );
                      },
                    ),
                  ),
                ],
              ),
            );
          } else {
            return Container();  // Alternatively, show a loading spinner or placeholder
          }
        },
      ),
    );
  }
}
