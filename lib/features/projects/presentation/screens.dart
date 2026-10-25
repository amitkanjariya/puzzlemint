import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../app/theme.dart';
import '../domain/project.dart';
import 'project_cubits.dart';

class ConnectionPage extends StatefulWidget {
  const ConnectionPage({super.key});
  @override
  State<ConnectionPage> createState() => _ConnectionPageState();
}

class _ConnectionPageState extends State<ConnectionPage> {
  final controller = TextEditingController();
  @override
  void dispose() { controller.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => Scaffold(body: Center(child: SingleChildScrollView(
    padding: const EdgeInsets.all(24), child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 480),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('PUZZLEMINT', style: TextStyle(color: MintColors.teal, fontWeight: FontWeight.w900, letterSpacing: 3)),
        const SizedBox(height: 28), Text('Turn any occasion into an adventure.', style: Theme.of(context).textTheme.displaySmall),
        const SizedBox(height: 16), const Text('Start the local backend and paste the session token printed in its terminal. Your projects stay on this computer.'),
        const SizedBox(height: 28), Card(child: Padding(padding: const EdgeInsets.all(24), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          const Text('CONNECT TO LOCAL STUDIO', style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 1.4, color: MintColors.muted)),
          const SizedBox(height: 18), TextField(controller: controller, obscureText: true, decoration: const InputDecoration(labelText: 'Session token'),
            onSubmitted: (_) => context.read<SessionCubit>().connect(controller.text)),
          const SizedBox(height: 16), BlocBuilder<SessionCubit, SessionState>(builder: (context, state) => Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            if (state.error.isNotEmpty) ErrorBanner(state.error),
            ElevatedButton(onPressed: state.loading ? null : () => context.read<SessionCubit>().connect(controller.text),
              child: state.loading ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Open studio')),
          ])),
        ]))),
        const SizedBox(height: 16), const Text('Backend: python backend/run.py  ·  Address: 127.0.0.1:8765', style: TextStyle(color: MintColors.muted)),
      ])))));
}

class StudioShell extends StatelessWidget {
  const StudioShell({super.key, required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, size) {
    final wide = size.maxWidth >= 880;
    return Scaffold(
      appBar: wide ? null : AppBar(title: const Text('PUZZLEMINT'), backgroundColor: MintColors.ink,
        foregroundColor: Colors.white, actions: [IconButton(onPressed: () => context.go('/'), icon: const Icon(Icons.dashboard_outlined)),
          IconButton(onPressed: () => context.go('/new'), icon: const Icon(Icons.add_circle_outline))]),
      body: Row(children: [
        if (wide) Container(width: 228, color: MintColors.ink, child: SafeArea(child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 32, 18, 20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('PUZZLEMINT', style: TextStyle(color: MintColors.gold, fontWeight: FontWeight.w900, letterSpacing: 2.2, fontSize: 18)),
            const SizedBox(height: 6), const Text('CREATOR STUDIO', style: TextStyle(color: Color(0xFF9CA7BE), letterSpacing: 2, fontSize: 10)),
            const SizedBox(height: 50), _nav(context, Icons.dashboard_outlined, 'Adventures', '/'),
            _nav(context, Icons.add_box_outlined, 'Create new', '/new'),
            const Spacer(), const Divider(color: Color(0xFF45506F)),
            const Padding(padding: EdgeInsets.all(12), child: Text('Local-first · Private by design', style: TextStyle(color: Color(0xFF9CA7BE), fontSize: 12))),
          ])))),
        Expanded(child: SafeArea(child: child)),
      ]),
    );
  });

  Widget _nav(BuildContext context, IconData icon, String title, String path) => Padding(
    padding: const EdgeInsets.only(bottom: 8), child: TextButton.icon(onPressed: () => context.go(path),
      icon: Icon(icon), label: Text(title), style: TextButton.styleFrom(foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12), alignment: Alignment.centerLeft)),
  );
}

class ErrorBanner extends StatelessWidget {
  const ErrorBanner(this.message, {super.key});
  final String message;
  @override
  Widget build(BuildContext context) => Container(width: double.infinity, margin: const EdgeInsets.only(bottom: 16), padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: const Color(0xFFFFECEE), borderRadius: BorderRadius.circular(10)),
    child: Row(children: [const Icon(Icons.error_outline, color: Color(0xFFD65C63)), const SizedBox(width: 10), Expanded(child: Text(message))]));
}

class StatusChip extends StatelessWidget {
  const StatusChip(this.status, {super.key});
  final String status;
  @override
  Widget build(BuildContext context) {
    final valid = status == 'validated' || status == 'exported';
    final color = valid ? const Color(0xFF147A5B) : status == 'validation_failed' ? const Color(0xFFB4424B) : MintColors.navy;
    return Container(padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6),
      decoration: BoxDecoration(color: color.withValues(alpha: .10), borderRadius: BorderRadius.circular(30)),
      child: Text(status.replaceAll('_', ' ').toUpperCase(), style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: .5)));
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});
  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  String search = '', filter = 'all';

  @override
  Widget build(BuildContext context) => StudioShell(child: SingleChildScrollView(padding: const EdgeInsets.all(32),
    child: Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1140), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('YOUR CREATIVE WORKSPACE', style: TextStyle(color: MintColors.teal, letterSpacing: 2, fontSize: 12, fontWeight: FontWeight.w900)),
        const SizedBox(height: 10), Text('Adventures', style: Theme.of(context).textTheme.displaySmall),
        const SizedBox(height: 8), const Text('Create an experience they will remember, then validate every clue before sharing.'),
        const SizedBox(height: 28), Wrap(spacing: 12, runSpacing: 12, children: [
          ElevatedButton.icon(onPressed: () => context.go('/new'), icon: const Icon(Icons.add), label: const Text('Create adventure')),
          OutlinedButton.icon(onPressed: () async {
            final id = await context.read<DashboardCubit>().createDemo();
            if (id != null && context.mounted) context.go('/project/$id');
          }, icon: const Icon(Icons.auto_stories_outlined), label: const Text('Create sample adventure')),
        ]),
        const SizedBox(height: 30), BlocBuilder<DashboardCubit, DashboardState>(builder: (context, state) {
          final visible = state.projects.where((project) =>
            (filter == 'all' || project.status == filter) &&
            ('${project.title} ${project.theme} ${project.occasion}'.toLowerCase().contains(search.toLowerCase()))).toList();
          return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            if (state.error.isNotEmpty) ErrorBanner(state.error),
            Row(children: [Expanded(child: TextField(onChanged: (value) => setState(() => search = value),
              decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Search adventures'))),
              const SizedBox(width: 12), DropdownButton<String>(value: filter, items: const [
                DropdownMenuItem(value: 'all', child: Text('All statuses')),
                DropdownMenuItem(value: 'draft', child: Text('Draft')),
                DropdownMenuItem(value: 'generated', child: Text('Generated')),
                DropdownMenuItem(value: 'validated', child: Text('Validated')),
                DropdownMenuItem(value: 'exported', child: Text('Exported')),
                DropdownMenuItem(value: 'validation_failed', child: Text('Needs repair')),
              ], onChanged: (value) => setState(() => filter = value!))]),
            const SizedBox(height: 24),
            if (state.loading) const Center(child: Padding(padding: EdgeInsets.all(48), child: CircularProgressIndicator())),
            if (!state.loading && visible.isEmpty) Card(child: Padding(padding: const EdgeInsets.all(38), child: Column(children: [
              const Icon(Icons.auto_awesome_outlined, size: 44, color: MintColors.teal), const SizedBox(height: 14),
              Text(state.projects.isEmpty ? 'Your first adventure starts here' : 'No adventures match', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8), const Text('Adjust the filters or create a new adventure.'),
            ]))),
            if (!state.loading) LayoutBuilder(builder: (context, constraints) => Wrap(spacing: 16, runSpacing: 16, children: visible.map((project) => SizedBox(
              width: constraints.maxWidth >= 700 ? (constraints.maxWidth - 16) / 2 : constraints.maxWidth,
              child: _ProjectCard(project: project, onDelete: () => _confirmDelete(context, project),
                onDuplicate: () async {
                  final id = await context.read<DashboardCubit>().duplicate(project.id);
                  if (id != null && context.mounted) context.go('/project/$id');
                }),
            )).toList())),
          ]);
        }),
      ])))));

  Future<void> _confirmDelete(BuildContext context, AdventureProject project) async {
    final cubit = context.read<DashboardCubit>();
    final confirmed = await showDialog<bool>(context: context, builder: (context) => AlertDialog(
      title: const Text('Delete adventure?'), content: Text('Delete “${project.title}” and its puzzles from local storage?'),
      actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete'))]));
    if (confirmed == true) await cubit.delete(project.id);
  }
}

class _ProjectCard extends StatelessWidget {
  const _ProjectCard({required this.project, required this.onDelete, required this.onDuplicate});
  final AdventureProject project;
  final VoidCallback onDelete;
  final VoidCallback onDuplicate;
  @override
  Widget build(BuildContext context) => Card(child: InkWell(borderRadius: BorderRadius.circular(18),
    onTap: () => context.go('/project/${project.id}'), child: Padding(padding: const EdgeInsets.all(24), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [const Icon(Icons.lock_open_rounded, color: MintColors.teal), const Spacer(), StatusChip(project.status)]),
        const SizedBox(height: 18), Text(project.title, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 6), Text('${project.occasion} · ${project.theme.toUpperCase()} · ${project.puzzleCount} puzzles', style: const TextStyle(color: MintColors.muted)),
        const SizedBox(height: 18), Row(children: [Text('For ${project.playerAlias}', style: const TextStyle(fontWeight: FontWeight.w600)),
          const Spacer(), IconButton(tooltip: 'Duplicate', onPressed: onDuplicate, icon: const Icon(Icons.copy_outlined)),
          IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline)),
          const Icon(Icons.arrow_forward_rounded, color: MintColors.teal)]),
      ]))));
}

class WizardPage extends StatelessWidget {
  const WizardPage({super.key});
  static const labels = ['Occasion', 'Theme', 'Personalize', 'Game style', 'Puzzles', 'Review', 'Generate'];

  @override
  Widget build(BuildContext context) => StudioShell(child: BlocBuilder<WizardCubit, WizardState>(builder: (context, state) {
    final cubit = context.read<WizardCubit>();
    return SingleChildScrollView(padding: const EdgeInsets.all(32), child: Center(child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 800), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('CREATE AN ADVENTURE', style: _eyebrow()), const SizedBox(height: 10),
        Text(labels[state.step], style: Theme.of(context).textTheme.displaySmall),
        const SizedBox(height: 12), Text('Step ${state.step + 1} of 7 · Your choices are saved as a local draft.'),
        const SizedBox(height: 18), LinearProgressIndicator(value: (state.step + 1) / 7, minHeight: 6,
          borderRadius: BorderRadius.circular(10), color: MintColors.teal, backgroundColor: const Color(0xFFE0DFDB)),
        const SizedBox(height: 24), Card(child: Padding(padding: const EdgeInsets.all(28), child: _wizardStep(context, state, cubit))),
        if (state.error.isNotEmpty) ErrorBanner(state.error),
        const SizedBox(height: 18), Row(children: [
          TextButton.icon(onPressed: state.step == 0 || state.busy ? null : cubit.back,
            icon: const Icon(Icons.arrow_back), label: const Text('Back')),
          const Spacer(), if (state.busy) const CircularProgressIndicator(),
          if (!state.busy && state.step < 6) ElevatedButton.icon(onPressed: () => cubit.next(),
            icon: const Icon(Icons.arrow_forward), label: const Text('Save and continue')),
          if (!state.busy && state.step == 6) ElevatedButton.icon(onPressed: () async {
            final id = await cubit.generate();
            if (id != null && context.mounted) context.go('/project/$id');
          }, icon: const Icon(Icons.auto_awesome), label: const Text('Generate adventure')),
        ]),
      ]))));
  }));

  Widget _wizardStep(BuildContext context, WizardState state, WizardCubit cubit) {
    final values = state.values;
    switch (state.step) {
      case 0:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('What are we celebrating?', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 18),
          TextFormField(initialValue: values['title'] as String, onChanged: (value) => cubit.setValue('title', value),
            maxLength: 120, decoration: const InputDecoration(labelText: 'Adventure title')),
          const SizedBox(height: 16), _choices('Occasion', values['occasion'] as String,
            const ['Birthday', 'Anniversary', 'Date night', 'Family night', 'Classroom', 'Celebration'], (value) => cubit.setValue('occasion', value)),
        ]);
      case 1:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Choose your world', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 12),
          for (final theme in const [('museum', 'Mystery Museum', 'Midnight galleries and a hidden diamond.'),
            ('agent', 'Secret Agent', 'Encoded transmissions and a missing dossier.'),
            ('library', 'Enchanted Library', 'Old books, lanterns, and hidden passages.')])
            Padding(padding: const EdgeInsets.only(bottom: 10), child: ListTile(
              title: Text(theme.$2), subtitle: Text(theme.$3),
              leading: Icon(values['theme'] == theme.$1 ? Icons.radio_button_checked : Icons.radio_button_off,
                color: MintColors.teal),
              onTap: () => cubit.setValue('theme', theme.$1),
              tileColor: const Color(0xFFF7F4EE), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)))),
        ]);
      case 2:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Make it theirs', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 6), const Text('A nickname is enough. No birthday or sensitive information is needed.'),
          const SizedBox(height: 18), TextFormField(initialValue: values['player_alias'] as String,
            onChanged: (value) => cubit.setValue('player_alias', value), maxLength: 60,
            decoration: const InputDecoration(labelText: 'Player nickname')),
          const SizedBox(height: 12), TextFormField(initialValue: values['final_message'] as String,
            onChanged: (value) => cubit.setValue('final_message', value), maxLength: 500, maxLines: 3,
            decoration: const InputDecoration(labelText: 'Final message')),
        ]);
      case 3:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Set the pace', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 18),
          _choices('Difficulty', values['difficulty'] as String, const ['easy', 'medium', 'hard'], (value) => cubit.setValue('difficulty', value)),
          const SizedBox(height: 26), Text('Target duration: ${values['duration_minutes']} minutes'),
          Slider(value: (values['duration_minutes'] as int).toDouble(), min: 10, max: 120, divisions: 11,
            label: '${values['duration_minutes']} min', onChanged: (value) => cubit.setValue('duration_minutes', value.round())),
        ]);
      case 4:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('How many chambers?', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 12),
          const Text('Each chamber contributes a clue and unlocks the next stage.'),
          const SizedBox(height: 18), SegmentedButton<int>(segments: const [
            ButtonSegment(value: 4, label: Text('4 · Basic')),
            ButtonSegment(value: 6, label: Text('6 · Premium')),
            ButtonSegment(value: 8, label: Text('8 · Custom'))],
            selected: {values['puzzle_count'] as int}, onSelectionChanged: (set) => cubit.setValue('puzzle_count', set.first)),
          const SizedBox(height: 18), Text('Generation seed: ${values['random_seed']}', style: const TextStyle(color: MintColors.muted)),
          TextButton.icon(onPressed: () => cubit.setValue('random_seed', DateTime.now().microsecondsSinceEpoch % 2147483647),
            icon: const Icon(Icons.shuffle), label: const Text('Shuffle variation')),
        ]);
      case 5:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Ready to create', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 12),
          for (final entry in values.entries) if (entry.key != 'random_seed') Padding(padding: const EdgeInsets.symmetric(vertical: 5),
            child: Row(children: [SizedBox(width: 160, child: Text(entry.key.replaceAll('_', ' ').toUpperCase(),
              style: _eyebrow())), Expanded(child: Text('${entry.value}'))])),
          const SizedBox(height: 12), const Text('The next step generates real puzzles. Run validation before exporting.'),
        ]);
      default:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Icon(Icons.auto_awesome, size: 46, color: MintColors.teal), const SizedBox(height: 18),
          Text('The adventure is ready to generate', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 10), const Text('PuzzleMint will build a connected sequence of cipher, number, logic, and ordering challenges using your choices.'),
          const SizedBox(height: 10), const Text('Your draft is saved, so you can return to it if generation is interrupted.'),
        ]);
    }
  }

  Widget _choices(String label, String value, List<String> options, ValueChanged<String> changed) =>
      DropdownButtonFormField<String>(initialValue: value, decoration: InputDecoration(labelText: label),
        items: options.map((item) => DropdownMenuItem(value: item, child: Text(item))).toList(),
        onChanged: (newValue) { if (newValue != null) changed(newValue); });
}

TextStyle _eyebrow() => const TextStyle(color: MintColors.teal, letterSpacing: 1.8, fontSize: 11, fontWeight: FontWeight.w900);

class DetailPage extends StatelessWidget {
  const DetailPage({super.key});

  @override
  Widget build(BuildContext context) => StudioShell(child: BlocBuilder<DetailCubit, DetailState>(builder: (context, state) {
    final cubit = context.read<DetailCubit>();
    final project = state.project;
    return SingleChildScrollView(padding: const EdgeInsets.all(32), child: Center(child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 1050), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        TextButton.icon(onPressed: () => context.go('/'), icon: const Icon(Icons.arrow_back), label: const Text('All adventures')),
        if (state.loading && project == null) const Center(child: Padding(padding: EdgeInsets.all(60), child: CircularProgressIndicator())),
        if (state.error.isNotEmpty) ErrorBanner(state.error),
        if (project != null) ...[
          const SizedBox(height: 12), Text('${project.occasion.toUpperCase()} · ${project.theme.toUpperCase()}', style: _eyebrow()),
          const SizedBox(height: 8), Wrap(crossAxisAlignment: WrapCrossAlignment.center, spacing: 16, runSpacing: 12, children: [
            Text(project.title, style: Theme.of(context).textTheme.displaySmall), StatusChip(project.status),
          ]),
          const SizedBox(height: 10), Text('For ${project.playerAlias} · ${project.durationMinutes} minutes · ${project.puzzleCount} chambers'),
          const SizedBox(height: 24), Wrap(spacing: 10, runSpacing: 10, children: [
            if (project.status == 'draft') OutlinedButton.icon(onPressed: () => context.go('/edit/${project.id}'),
              icon: const Icon(Icons.edit_note), label: const Text('Continue setup')),
            if (state.puzzles.isEmpty) ElevatedButton.icon(onPressed: state.busy ? null : cubit.generate,
              icon: const Icon(Icons.auto_awesome), label: const Text('Generate puzzles')),
            if (state.puzzles.isNotEmpty) ...[
              ElevatedButton.icon(onPressed: state.busy ? null : cubit.validate,
                icon: const Icon(Icons.verified_outlined), label: const Text('Run validation')),
              if (project.status == 'validation_failed') OutlinedButton.icon(onPressed: state.busy ? null : cubit.repair,
                icon: const Icon(Icons.healing_outlined), label: const Text('Repair issues')),
              OutlinedButton.icon(onPressed: state.busy ? null : () => _confirmRegenerate(context, cubit),
                icon: const Icon(Icons.refresh), label: const Text('Regenerate all')),
              OutlinedButton.icon(onPressed: state.busy || !{'validated', 'exported'}.contains(project.status) ? null : cubit.exportHtml,
                icon: const Icon(Icons.web_outlined), label: const Text('Export offline game')),
              OutlinedButton.icon(onPressed: state.busy || !{'validated', 'exported'}.contains(project.status) ? null : cubit.exportPdf,
                icon: const Icon(Icons.picture_as_pdf_outlined), label: const Text('Export PDFs')),
            ],
          ]),
          if (state.busy) const Padding(padding: EdgeInsets.only(top: 16), child: LinearProgressIndicator()),
          if (state.notice.isNotEmpty) Container(width: double.infinity, margin: const EdgeInsets.only(top: 18),
            padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: const Color(0xFFE6F5F1), borderRadius: BorderRadius.circular(12)),
            child: SelectableText(state.notice)),
          if (state.validation != null && state.validation!['passed'] == false) Card(child: Padding(padding: const EdgeInsets.all(20),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Validation report', style: Theme.of(context).textTheme.titleLarge),
              for (final issue in state.validation!['errors'] as List) Padding(padding: const EdgeInsets.only(top: 8),
                child: Text('${issue['code']}: ${issue['message']}')),
            ]))),
          const SizedBox(height: 32), Text('Puzzle path', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 6), const Text('Every chamber depends on the one before it. Inspect clues and edit presentation text here.'),
          const SizedBox(height: 14),
          if (state.puzzles.isEmpty) const Card(child: Padding(padding: EdgeInsets.all(30), child: Text('This draft has no puzzles yet. Generate an adventure to begin.'))),
          for (final puzzle in state.puzzles) _PuzzleCard(puzzle: puzzle,
            onEdit: () => _editPuzzle(context, cubit, puzzle),
            onRegenerate: () => _confirmReplace(context, cubit, puzzle)),
        ],
      ]))));
  }));

  Future<void> _confirmRegenerate(BuildContext context, DetailCubit cubit) async {
    final confirmed = await showDialog<bool>(context: context, builder: (context) => AlertDialog(
      title: const Text('Regenerate all puzzles?'),
      content: const Text('This replaces all current puzzles and their edits. The same seed reproduces the same puzzle data.'),
      actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Regenerate'))]));
    if (confirmed == true) await cubit.generate();
  }

  Future<void> _editPuzzle(BuildContext context, DetailCubit cubit, AdventurePuzzle puzzle) async {
    final title = TextEditingController(text: puzzle.title);
    final story = TextEditingController(text: puzzle.parameters['story'] as String? ?? '');
    final saved = await showDialog<bool>(context: context, builder: (context) => AlertDialog(
      title: const Text('Edit chamber'), content: SizedBox(width: 500, child: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: title, maxLength: 120, decoration: const InputDecoration(labelText: 'Title')),
        const SizedBox(height: 12), TextField(controller: story, maxLength: 1000, maxLines: 4,
          decoration: const InputDecoration(labelText: 'Story text')),
      ])), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Save'))]));
    if (saved == true) await cubit.editPuzzle(puzzle.id, title.text, story.text);
    title.dispose(); story.dispose();
  }

  Future<void> _confirmReplace(BuildContext context, DetailCubit cubit, AdventurePuzzle puzzle) async {
    final confirmed = await showDialog<bool>(context: context, builder: (context) => AlertDialog(
      title: const Text('Replace this chamber?'),
      content: Text('Replace “${puzzle.title}” with a fresh valid puzzle. Other chambers will stay as they are.'),
      actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Replace'))]));
    if (confirmed == true) await cubit.regeneratePuzzle(puzzle.id);
  }
}

class _PuzzleCard extends StatelessWidget {
  const _PuzzleCard({required this.puzzle, required this.onEdit, required this.onRegenerate});
  final AdventurePuzzle puzzle;
  final VoidCallback onEdit, onRegenerate;

  @override
  Widget build(BuildContext context) => Card(margin: const EdgeInsets.only(bottom: 12), child: ExpansionTile(
    leading: CircleAvatar(backgroundColor: MintColors.navy, foregroundColor: Colors.white, child: Text('${puzzle.position + 1}')),
    title: Text(puzzle.title, style: const TextStyle(fontWeight: FontWeight.w700)),
    subtitle: Text('${puzzle.type.replaceAll('_', ' ').toUpperCase()} · ${puzzle.validationStatus}'),
    childrenPadding: const EdgeInsets.fromLTRB(24, 0, 24, 22),
    expandedCrossAxisAlignment: CrossAxisAlignment.start, children: [
      const Divider(), Text(puzzle.parameters['story'] as String? ?? ''), const SizedBox(height: 8),
      Text(puzzle.parameters['prompt'] as String? ?? ''),
      if (puzzle.type == 'cipher') _clue('Inscription: ${puzzle.parameters['ciphertext']}'),
      if (puzzle.type == 'logic_grid') for (final clue in (puzzle.parameters['clue_texts'] as List? ?? [])) _clue('$clue'),
      if (puzzle.type == 'sequence') for (final edge in (puzzle.parameters['edges'] as List)) _clue('${edge[0]} before ${edge[1]}'),
      const SizedBox(height: 10), Text('Answer: ${puzzle.solution['answer']}', style: const TextStyle(fontWeight: FontWeight.w700)),
      const SizedBox(height: 10), Text('Requires ${puzzle.dependencies.isEmpty ? 'no earlier chamber' : 'the previous chamber'}',
        style: const TextStyle(color: MintColors.muted)),
      const SizedBox(height: 10), for (var index = 0; index < puzzle.hints.length; index++)
        Text('Hint ${index + 1}: ${puzzle.hints[index]}'),
      const SizedBox(height: 12), Wrap(spacing: 8, runSpacing: 8, children: [
        OutlinedButton.icon(onPressed: onEdit, icon: const Icon(Icons.edit_outlined), label: const Text('Edit title and story')),
        OutlinedButton.icon(onPressed: onRegenerate, icon: const Icon(Icons.autorenew), label: const Text('Replace puzzle')),
      ]),
    ],
  ));

  Widget _clue(String value) => Container(width: double.infinity, margin: const EdgeInsets.only(top: 8),
    padding: const EdgeInsets.all(10), decoration: const BoxDecoration(color: Color(0xFFF7F4EE),
      border: Border(left: BorderSide(color: MintColors.gold, width: 3))), child: Text(value));
}
