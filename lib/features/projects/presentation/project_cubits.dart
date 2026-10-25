import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/api_client.dart';
import '../domain/project.dart';

class SessionState {
  const SessionState({this.connected = false, this.loading = false, this.error = ''});
  final bool connected, loading;
  final String error;
}

class SessionCubit extends Cubit<SessionState> {
  SessionCubit(this._api, this._repository) : super(const SessionState());
  final ApiClient _api;
  final ProjectRepository _repository;

  Future<void> connect(String token) async {
    emit(const SessionState(loading: true));
    _api.setToken(token.trim());
    try {
      await _repository.list();
      emit(const SessionState(connected: true));
    } catch (error) {
      emit(SessionState(error: readableError(error)));
    }
  }
}

class DashboardState {
  const DashboardState({this.projects = const [], this.loading = false, this.error = ''});
  final List<AdventureProject> projects;
  final bool loading;
  final String error;
}

class DashboardCubit extends Cubit<DashboardState> {
  DashboardCubit(this._repository) : super(const DashboardState());
  final ProjectRepository _repository;

  Future<void> load() async {
    emit(const DashboardState(loading: true));
    try {
      emit(DashboardState(projects: await _repository.list()));
    } catch (error) {
      emit(DashboardState(error: readableError(error)));
    }
  }

  Future<void> delete(String id) async {
    try {
      await _repository.delete(id);
      await load();
    } catch (error) {
      emit(DashboardState(projects: state.projects, error: readableError(error)));
    }
  }

  Future<String?> duplicate(String id) async {
    try {
      final copy = await _repository.duplicate(id);
      await load();
      return copy.id;
    } catch (error) {
      emit(DashboardState(projects: state.projects, error: readableError(error)));
      return null;
    }
  }

  Future<String?> createDemo() async {
    try {
      final project = await _repository.create({
        'title': 'The Midnight Museum', 'theme': 'museum', 'occasion': 'Birthday',
        'difficulty': 'medium', 'duration_minutes': 30, 'puzzle_count': 6,
        'random_seed': 42, 'player_alias': 'Aarav',
        'final_message': 'Happy Birthday, Aarav! You recovered the Star Diamond.',
      });
      await _repository.generate(project.id);
      await _repository.validate(project.id);
      await load();
      return project.id;
    } catch (error) {
      emit(DashboardState(projects: state.projects, error: readableError(error)));
      return null;
    }
  }
}

class WizardState {
  const WizardState({required this.values, this.step = 0, this.projectId, this.busy = false, this.error = ''});
  final Map<String, dynamic> values;
  final int step;
  final String? projectId;
  final bool busy;
  final String error;

  WizardState copy({Map<String, dynamic>? values, int? step, String? projectId, bool? busy, String? error}) =>
      WizardState(values: values ?? this.values, step: step ?? this.step,
        projectId: projectId ?? this.projectId, busy: busy ?? this.busy, error: error ?? this.error);
}

class WizardCubit extends Cubit<WizardState> {
  WizardCubit(this._repository) : super(const WizardState(values: {
    'title': 'A New Adventure', 'occasion': 'Birthday', 'theme': 'museum',
    'player_alias': 'Explorer', 'final_message': 'What an adventure!',
    'difficulty': 'medium', 'duration_minutes': 30, 'puzzle_count': 6,
    'random_seed': 42,
  }));
  final ProjectRepository _repository;

  Future<void> loadDraft(String id) async {
    emit(state.copy(busy: true));
    try {
      final project = await _repository.get(id);
      emit(state.copy(projectId: id, busy: false, values: {
        'title': project.title, 'occasion': project.occasion, 'theme': project.theme,
        'player_alias': project.playerAlias, 'final_message': project.finalMessage,
        'difficulty': project.difficulty, 'duration_minutes': project.durationMinutes,
        'puzzle_count': project.puzzleCount, 'random_seed': project.randomSeed,
      }));
    } catch (error) {
      emit(state.copy(busy: false, error: readableError(error)));
    }
  }

  void setValue(String key, dynamic value) => emit(state.copy(values: {...state.values, key: value}, error: ''));
  void back() { if (state.step > 0) emit(state.copy(step: state.step - 1, error: '')); }

  Future<bool> next() async {
    final values = state.values;
    if (state.step == 0 && (values['title'] as String).trim().length < 3) {
      emit(state.copy(error: 'Give the adventure a title of at least 3 characters.'));
      return false;
    }
    emit(state.copy(busy: true, error: ''));
    try {
      String? id = state.projectId;
      if (id == null) {
        id = (await _repository.create(values)).id;
      } else {
        await _repository.update(id, values);
      }
      emit(state.copy(projectId: id, step: state.step + 1, busy: false));
      return true;
    } catch (error) {
      emit(state.copy(busy: false, error: readableError(error)));
      return false;
    }
  }

  Future<String?> generate() async {
    emit(state.copy(busy: true, error: ''));
    try {
      final id = state.projectId!;
      await _repository.update(id, state.values);
      await _repository.generate(id);
      emit(state.copy(busy: false));
      return id;
    } catch (error) {
      emit(state.copy(busy: false, error: readableError(error)));
      return null;
    }
  }
}

class DetailState {
  const DetailState({this.project, this.puzzles = const [], this.loading = false,
    this.busy = false, this.error = '', this.notice = '', this.validation});
  final AdventureProject? project;
  final List<AdventurePuzzle> puzzles;
  final bool loading, busy;
  final String error, notice;
  final Map<String, dynamic>? validation;

  DetailState copy({AdventureProject? project, List<AdventurePuzzle>? puzzles, bool? loading,
    bool? busy, String? error, String? notice, Map<String, dynamic>? validation, bool clearValidation = false}) => DetailState(
      project: project ?? this.project, puzzles: puzzles ?? this.puzzles,
      loading: loading ?? this.loading, busy: busy ?? this.busy,
      error: error ?? this.error, notice: notice ?? this.notice,
      validation: clearValidation ? null : validation ?? this.validation);
}

class DetailCubit extends Cubit<DetailState> {
  DetailCubit(this._repository, this.id) : super(const DetailState());
  final ProjectRepository _repository;
  final String id;

  Future<void> load() async {
    emit(state.copy(loading: true, error: ''));
    try {
      final project = await _repository.get(id);
      final puzzles = await _repository.puzzles(id);
      emit(state.copy(project: project, puzzles: puzzles, loading: false));
    } catch (error) {
      emit(state.copy(loading: false, error: readableError(error)));
    }
  }

  Future<void> generate() => _act(() async {
    await _repository.generate(id);
    await load();
    emit(state.copy(notice: 'Adventure generated. Run validation before exporting.'));
  });

  Future<void> validate() => _act(() async {
    final result = await _repository.validate(id);
    await load();
    emit(state.copy(validation: result, notice: result['passed'] == true ? 'Every puzzle and dependency passed validation.' : 'Validation found issues. Review the report below.'));
  });

  Future<void> repair() => _act(() async {
    final result = await _repository.repair(id);
    await load();
    emit(state.copy(validation: result, notice: result['passed'] == true
      ? 'Invalid puzzles were repaired and the full adventure passed validation.'
      : 'Repair reached its attempt limit. Review the remaining issues.'));
  });

  Future<void> regeneratePuzzle(String puzzleId) => _act(() async {
    await _repository.regeneratePuzzle(puzzleId);
    await load();
    emit(state.copy(clearValidation: true, notice: 'Chamber replaced. Revalidate before exporting.'));
  });

  Future<void> exportHtml() => _act(() async {
    final result = await _repository.exportHtml(id);
    await load();
    emit(state.copy(notice: 'Offline game saved: ${result['path']}'));
  });

  Future<void> exportPdf() => _act(() async {
    final result = await _repository.exportPdf(id);
    await load();
    emit(state.copy(notice: 'Player PDF: ${result['handout']['path']}\nAnswer key: ${result['answer_key']['path']}'));
  });

  Future<void> editPuzzle(String puzzleId, String title, String story) => _act(() async {
    await _repository.updatePuzzle(puzzleId, {'title': title, 'prompt': story});
    await load();
    emit(state.copy(notice: 'Puzzle saved. Revalidate before exporting.'));
  });

  Future<void> _act(Future<void> Function() action) async {
    emit(state.copy(busy: true, error: '', notice: ''));
    try {
      await action();
      emit(state.copy(busy: false));
    } catch (error) {
      emit(state.copy(busy: false, error: readableError(error)));
    }
  }
}
