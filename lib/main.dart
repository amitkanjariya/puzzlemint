import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';

import 'app/theme.dart';
import 'core/api_client.dart';
import 'features/projects/data/api_project_repository.dart';
import 'features/projects/domain/project.dart';
import 'features/projects/presentation/project_cubits.dart';
import 'features/projects/presentation/screens.dart';

void main() {
  final services = GetIt.instance;
  services.registerSingleton<ApiClient>(ApiClient());
  services.registerSingleton<ProjectRepository>(ApiProjectRepository(services<ApiClient>()));
  runApp(BlocProvider(
    create: (_) => SessionCubit(services<ApiClient>(), services<ProjectRepository>()),
    child: const PuzzleMintApp(),
  ));
}

class PuzzleMintApp extends StatefulWidget {
  const PuzzleMintApp({super.key});

  @override
  State<PuzzleMintApp> createState() => _PuzzleMintAppState();
}

class _PuzzleMintAppState extends State<PuzzleMintApp> {
  late final GoRouter _router = GoRouter(routes: [
    GoRoute(path: '/', builder: (context, state) => BlocProvider(
      create: (_) => DashboardCubit(GetIt.instance<ProjectRepository>())..load(),
      child: const DashboardPage(),
    )),
    GoRoute(path: '/new', builder: (context, state) => BlocProvider(
      create: (_) => WizardCubit(GetIt.instance<ProjectRepository>()),
      child: const WizardPage(),
    )),
    GoRoute(path: '/edit/:id', builder: (context, state) => BlocProvider(
      create: (_) => WizardCubit(GetIt.instance<ProjectRepository>())..loadDraft(state.pathParameters['id']!),
      child: const WizardPage(),
    )),
    GoRoute(path: '/project/:id', builder: (context, state) => BlocProvider(
      create: (_) => DetailCubit(GetIt.instance<ProjectRepository>(), state.pathParameters['id']!)..load(),
      child: const DetailPage(),
    )),
  ]);

  @override
  Widget build(BuildContext context) => BlocBuilder<SessionCubit, SessionState>(
    builder: (context, session) => session.connected
        ? MaterialApp.router(title: 'PuzzleMint', debugShowCheckedModeBanner: false,
            theme: mintTheme(), routerConfig: _router)
        : MaterialApp(title: 'PuzzleMint', debugShowCheckedModeBanner: false,
            theme: mintTheme(), home: const ConnectionPage()),
  );
}
