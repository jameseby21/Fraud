"""Interactive encrypted notes. No note content is accepted in shell arguments."""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from uuid import uuid4

from vault import VaultError, VaultFile, _prompt, default_vault_path

KINDS = ('observation', 'hypothesis', 'counterevidence', 'review_note')


def _text(value, maximum, field):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise VaultError(f'Invalid {field}.')
    if any((ord(c) < 32 and c not in '\n\t') or 127 <= ord(c) <= 159 for c in value):
        raise VaultError(f'Control characters are not allowed in {field}.')
    return value


def _case(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', value):
        raise VaultError('Use a short case identifier with letters, digits, dots, underscores, or hyphens.')
    return value


def _timestamp(now):
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise VaultError('A timezone-aware timestamp is required.')
    return now.astimezone(timezone.utc).isoformat()


def _document(store, phrase):
    document = store.read(phrase)
    seen = set()
    for note in document['notes']:
        if not isinstance(note, dict) or not isinstance(note.get('id'), str) or note['id'] in seen:
            raise VaultError('Invalid note document.')
        seen.add(note['id'])
        _case(note.get('case_id'))
        _text(note.get('title'), 200, 'title')
        if note.get('kind') not in KINDS:
            raise VaultError('Invalid note type.')
        revisions = note.get('revisions')
        if not isinstance(revisions, list) or not revisions:
            raise VaultError('Invalid note history.')
        for number, revision in enumerate(revisions, 1):
            if not isinstance(revision, dict) or type(revision.get('number')) is not int or revision['number'] != number:
                raise VaultError('Invalid note revision sequence.')
            _text(revision.get('body'), 20000, 'note body')
            _text(revision.get('reason'), 500, 'correction reason')
            try:
                _timestamp(datetime.fromisoformat(revision['recorded_at']))
            except (TypeError, ValueError, KeyError):
                raise VaultError('Invalid note timestamp.') from None
    return document


def _find(document, identifier):
    for note in document['notes']:
        if note['id'] == identifier:
            return note
    raise VaultError('Unknown note.')


def add_note(store, phrase, case_id, kind, title, body, now=None):
    _case(case_id)
    _text(title, 200, 'title')
    _text(body, 20000, 'note body')
    if kind not in KINDS:
        raise VaultError('Choose an observation, hypothesis, counterevidence, or review_note.')
    timestamp = _timestamp(now)
    document = _document(store, phrase)
    identifier = str(uuid4())
    document['notes'].append(dict(id=identifier, case_id=case_id, kind=kind, title=title,
                                  revisions=[dict(number=1, body=body, reason='Created', recorded_at=timestamp)]))
    store.update(phrase, document, expected_revision=document['revision'])
    return identifier


def revise_note(store, phrase, identifier, body, reason, expected_revision, now=None):
    _text(body, 20000, 'note body')
    _text(reason, 500, 'correction reason')
    timestamp = _timestamp(now)
    document = _document(store, phrase)
    note = _find(document, identifier)
    if type(expected_revision) is not int or note['revisions'][-1]['number'] != expected_revision:
        raise VaultError('Note changed; reload before submitting a correction.')
    note['revisions'].append(dict(number=expected_revision+1, body=body, reason=reason, recorded_at=timestamp))
    store.update(phrase, document, expected_revision=document['revision'])


def read_note(store, phrase, identifier):
    return copy.deepcopy(_find(_document(store, phrase), identifier))


def list_notes(store, phrase):
    return [dict(id=n['id'], case_id=n['case_id'], kind=n['kind'], title=n['title'],
                 revision=n['revisions'][-1]['number'], updated_at=n['revisions'][-1]['recorded_at'])
            for n in _document(store, phrase)['notes']]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('add', 'list', 'read', 'revise'))
    parser.add_argument('note_id', nargs='?')
    parser.add_argument('--history', action='store_true', help='Explicitly display all earlier bodies and correction reasons with read')
    parser.add_argument('--path', type=Path, default=default_vault_path())
    args = parser.parse_args(argv)
    try:
        store = VaultFile(args.path)
        phrase = _prompt('Vault passphrase: ')
        if args.command == 'add':
            case = _prompt('Case identifier (hidden): ')
            kind = _prompt('Type: observation / hypothesis / counterevidence / review_note (hidden): ')
            title = _prompt('Title (hidden): ')
            body = _prompt('Note body (hidden, one line): ')
            identifier = add_note(store, phrase, case, kind, title, body)
            print('Encrypted note saved. ID: ' + identifier)
        elif args.command == 'list':
            print(json.dumps(list_notes(store, phrase), indent=2))
        elif args.command == 'read':
            note = read_note(store, phrase, args.note_id)
            if not args.history:
                note = dict(id=note['id'], case_id=note['case_id'], kind=note['kind'], title=note['title'],
                            current=note['revisions'][-1])
            print(json.dumps(note, indent=2))
        else:
            note = read_note(store, phrase, args.note_id)
            body = _prompt('Corrected note body (hidden, one line): ')
            reason = _prompt('Correction reason (hidden): ')
            revise_note(store, phrase, args.note_id, body, reason, expected_revision=note['revisions'][-1]['number'])
            print('Encrypted correction saved; earlier versions retained.')
        return 0
    except (VaultError, OSError):
        print('Encrypted note operation failed. Check input, passphrase, permissions, or revision state.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
