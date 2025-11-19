from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, REFS_DIR, TAGS_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def _create_commit(repo: Repository) -> str:
    sample = repo.working_dir / 'sample.txt'
    sample.write_text('sample content')
    return repo.commit_working_dir('Author', 'Message')


def test_create_tag_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)
    capsys.readouterr()

    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir,
                                   tag_name='v1.0',
                                   commit=str(commit_ref)) == 0

    output = capsys.readouterr().out
    assert 'Tag "v1.0"' in output
    assert temp_repo.tag_exists('v1.0')


def test_create_tag_invalid_ref(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    capsys.readouterr()
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir,
                                   tag_name='bad',
                                   commit='does-not-exist') == -1

    assert 'Repository error' in capsys.readouterr().err


def test_create_tag_duplicate(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)
    temp_repo.add_tag('dup', commit_ref)

    capsys.readouterr()
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir,
                                   tag_name='dup',
                                   commit=str(commit_ref)) == -1
    assert 'Repository error' in capsys.readouterr().err


def test_create_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(working_dir_path=temp_repo_dir,
                                   tag_name='v1',
                                   commit='HEAD') == -1
    assert 'No repository found' in capsys.readouterr().err


def test_tags_command_lists_tags(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)
    temp_repo.add_tag('v1', commit_ref)
    temp_repo.add_tag('v2', commit_ref)

    capsys.readouterr()
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    output = capsys.readouterr().out
    assert 'Tags:' in output
    assert 'v1:' in output
    assert 'v2:' in output


def test_tags_command_no_tags(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    tags_dir = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR
    if tags_dir.exists():
        for entry in tags_dir.iterdir():
            entry.unlink()

    capsys.readouterr()
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    assert 'No tags found' in capsys.readouterr().out


def test_tags_command_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.tags(working_dir_path=temp_repo_dir) == -1
    assert 'No repository found' in capsys.readouterr().err


def test_delete_tag_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)
    temp_repo.add_tag('release', commit_ref)

    capsys.readouterr()
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir,
                                   tag_name='release') == 0
    assert 'deleted' in capsys.readouterr().out
    assert not temp_repo.tag_exists('release')


def test_delete_tag_missing(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    capsys.readouterr()
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir,
                                   tag_name='ghost') == -1
    assert 'Repository error' in capsys.readouterr().err


def test_delete_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo_dir,
                                   tag_name='ghost') == -1
    assert 'No repository found' in capsys.readouterr().err

