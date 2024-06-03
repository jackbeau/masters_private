import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/bloc/sidebar_bloc.dart';
import '../../data/repositories/speech_repository.dart';

class Sidebar extends StatelessWidget {
  const Sidebar({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider<SidebarBloc>(
      create: (context) => SidebarBloc(RepositoryProvider.of<SpeechRepository>(context))..add(LoadActs()),
      child: BlocBuilder<SidebarBloc, SidebarState>(
        builder: (context, state) {
          if (state is SidebarLoaded) {
            return Container(
              width: 200,
              color: Colors.blueGrey[900],
              padding: const EdgeInsets.all(8.0),
              child: Column(
                children: [
                  const Text('House Open', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                  const Divider(color: Colors.grey),
                  const Text('Running Time', style: TextStyle(color: Colors.grey, fontSize: 16)),
                  const Text('00:17:27', style: TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Act Up', style: TextStyle(color: Colors.grey, fontSize: 14)),
                          Text('00:17:27', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Local Time', style: TextStyle(color: Colors.grey, fontSize: 14)),
                          Text(state.currentTime, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () {
                      context.read<SidebarBloc>().add(StartSpeechToLine());
                    },
                    child: const Text('Start'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      context.read<SidebarBloc>().add(StopSpeechToLine());
                    },
                    child: const Text('Stop'),
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