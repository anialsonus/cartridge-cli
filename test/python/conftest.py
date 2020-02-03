import py
import pytest
import tempfile
import shutil
import os

from project import Project
from project import remove_dependency
from project import add_dependency_submodule
from project import use_deprecated_files
from project import remove_all_dependencies


# ########
# Fixtures
# ########
@pytest.fixture(scope='module')
def module_tmpdir(request):
    dir = py.path.local(tempfile.mkdtemp())
    request.addfinalizer(lambda: dir.remove(rec=1))
    return str(dir)


# ################
# Project fixtures
# ################
# There are three main types of projects:
# * light_project ({original,deprecated}_light_project):
#   Cartridge CLI creates project with cartridge dependency by default.
#   It's known that installing cartridge rocks is a long operation,
#   so we don't want to perform it on every test.
#   These fixtures are used to decrease packing time.
#   They don't have a cartridge dependency,
#   but have dependency installed from submodule
#   (see add_dependency_submodule function for details)
#   In fact, we need to install cartridge dependency only
#   for e2e
#
# * project_with_cartridge ({original,deprecated}_project_with_cartridge):
#   This is a project with cartridge dependency installed.
#   Is used in `docker pack` tests. Test image is built once and then
#   it's used in all docker tests include e2e.
#   This project also have submodule dependency (see add_dependency_submodule)
#   to test pre and post build hooks
#
# * project_without_dependencies:
#   This is the empty project without dependencies.
#   It is used for error behavior tests and tests where
#   result package content doesn't matter
#
################
# Light projects
################
@pytest.fixture(scope="module")
def original_light_project(module_tmpdir):
    project = Project('light-original-project', module_tmpdir, 'cartridge')

    remove_dependency(project, 'cartridge')
    remove_dependency(project, 'luatest')

    add_dependency_submodule(project)

    return project


@pytest.fixture(scope="module")
def deprecated_light_project(module_tmpdir):
    project = Project('light-deprecated-project', module_tmpdir, 'cartridge')

    remove_dependency(project, 'cartridge')
    remove_dependency(project, 'luatest')

    add_dependency_submodule(project)

    use_deprecated_files(project)

    return project


@pytest.fixture(scope="module", params=['original', 'deprecated'])
def light_project(original_light_project, deprecated_light_project, request):
    if request.param == 'original':
        return original_light_project
    elif request.param == 'deprecated':
        return deprecated_light_project


#########################
# Projects with cartridge
#########################
@pytest.fixture(scope="module")
def original_project_with_cartridge(module_tmpdir):
    project = Project('original-project-with-cartridge', module_tmpdir, 'cartridge')
    remove_dependency(project, 'luatest')

    add_dependency_submodule(project)

    return project


@pytest.fixture(scope="module")
def deprecated_project_with_cartridge(module_tmpdir):
    project = Project('deprecated-project-with-cartridge', module_tmpdir, 'cartridge')
    remove_dependency(project, 'luatest')

    add_dependency_submodule(project)
    use_deprecated_files(project)

    return project


@pytest.fixture(scope="module", params=['original', 'deprecated'])
def project_with_cartridge(original_project_with_cartridge, deprecated_project_with_cartridge, request):
    if request.param == 'original':
        return original_project_with_cartridge
    elif request.param == 'deprecated':
        return deprecated_project_with_cartridge


##############################
# Project without dependencies
##############################
@pytest.fixture(scope="module")
def project_without_dependencies(module_tmpdir):
    project = Project('empty-project', module_tmpdir, 'cartridge')

    remove_all_dependencies(project)
    return project


#####################
# Project without git
#####################
@pytest.fixture(scope="module")
def project_without_git(module_tmpdir):
    project = Project('project-without-git', module_tmpdir, 'cartridge')

    remove_all_dependencies(project)
    shutil.rmtree(os.path.join(project.path, '.git'))

    return project


########################
# Project with .git file
########################
@pytest.fixture(scope="module")
def project_with_git_file(module_tmpdir):
    project = Project('project-with-git-file', module_tmpdir, 'cartridge')

    remove_all_dependencies(project)
    shutil.rmtree(os.path.join(project.path, '.git'))

    git_filepath = os.path.join(project.path, '.git')
    with open(git_filepath, 'w') as f:
        f.write("I am .git file")

    return project


#############################
# Project with wrong filemode
#############################
@pytest.fixture(scope="module")
def project_with_wrong_filemode(module_tmpdir):
    project = Project('project-with-wrong-filemode', module_tmpdir, 'cartridge')

    remove_all_dependencies(project)

    # add file with invalid (700) mode
    filepath = os.path.join(project.path, 'wrong-mode-file.lua')
    with open(filepath, 'w') as f:
        f.write("return 'My filemode is wrong'")
    os.chmod(filepath, 0o700)

    return project
