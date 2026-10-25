import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:puzzlemint/core/api_client.dart';
import 'package:puzzlemint/features/projects/data/api_project_repository.dart';
import 'package:puzzlemint/features/projects/domain/project.dart';
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

  test('wizard rejects a short title and persists a valid draft', () async {
    final repository = _WizardRepository();
    final cubit = WizardCubit(repository);
    cubit.setValue('title', 'X');
    expect(await cubit.next(), isFalse);
    expect(repository.creates, 0);
    cubit.setValue('title', 'Museum Night');
    expect(await cubit.next(), isTrue);
    expect(cubit.state.step, 1);
    expect(cubit.state.projectId, 'draft-1');
    cubit.setValue('theme', 'agent');
    expect(await cubit.next(), isTrue);
    expect(repository.updates, 1);
    await cubit.close();
  });

  testWidgets('wizard advances from occasion to theme', (tester) async {
    final repository = _WizardRepository();
    await tester.pumpWidget(BlocProvider(
      create: (_) => WizardCubit(repository),
      child: const MaterialApp(home: WizardPage()),
    ));
    expect(find.text('What are we celebrating?'), findsOneWidget);
    await tester.ensureVisible(find.text('Save and continue'));
    await tester.tap(find.text('Save and continue'));
    await tester.pumpAndSettle();
    expect(find.text('Choose your world'), findsOneWidget);
  });
}

class _WizardRepository implements ProjectRepository {
  int creates = 0, updates = 0;
  AdventureProject? saved;

  @override
  Future<AdventureProject> create(Map<String, dynamic> values) async {
    creates++;
    saved = AdventureProject.fromJson({...values, 'id': 'draft-1', 'status': 'draft'});
    return saved!;
  }

  @override
  Future<AdventureProject> update(String id, Map<String, dynamic> values) async {
    updates++;
    saved = AdventureProject.fromJson({...values, 'id': id, 'status': 'draft'});
    return saved!;
  }

  @override
  Future<AdventureProject> get(String id) async => saved!;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
