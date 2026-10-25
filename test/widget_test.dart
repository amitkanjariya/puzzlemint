import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:puzzlemint/core/api_client.dart';
import 'package:puzzlemint/features/projects/data/api_project_repository.dart';
import 'package:puzzlemint/features/projects/presentation/project_cubits.dart';
import 'package:puzzlemint/features/projects/presentation/screens.dart';

void main() {
  testWidgets('local session screen explains how to connect', (tester) async {
    final api = ApiClient();
    await tester.pumpWidget(BlocProvider(
      create: (_) => SessionCubit(api, ApiProjectRepository(api)),
      child: const MaterialApp(home: ConnectionPage()),
    ));
    expect(find.text('PUZZLEMINT'), findsOneWidget);
    expect(find.text('Session token'), findsOneWidget);
    expect(find.text('Open studio'), findsOneWidget);
  });
}
