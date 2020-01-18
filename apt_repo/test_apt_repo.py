from apt_repo import *

repo = APTRepository.from_sources_list_entry("deb http://archive.ubuntu.com/ubuntu bionic main")
flat_repo = APTRepository.from_sources_list_entry("deb https://pkg.jenkins.io/debian/ binary")

def test_from_sources_list_entry():
    repo = APTRepository.from_sources_list_entry("deb http://archive.ubuntu.com/ubuntu bionic main")

    assert repo.url == "http://archive.ubuntu.com/ubuntu"
    assert repo.dist == "bionic"
    assert repo.components == ["main"]

def test_packages():
    repo.packages

def test_release_file():
    repo.release_file

def test_release_file():
    repo.all_components

def test_get_binary_packages_by_component():
    repo.get_binary_packages_by_component("restricted")

def test_get_packages_by_name():
    repo.get_packages_by_name("htop")

def test_get_package():
    version = repo.get_packages_by_name("htop")[0].version
    repo.get_package("htop", version)

def test_get_package_url():
    version = repo.get_packages_by_name("htop")[0].version
    repo.get_package_url("htop", version)

def test_flat_repo_from_sources_list_entry():
    repo = APTRepository.from_sources_list_entry("deb https://pkg.jenkins.io/debian/ binary")

    assert repo.url == "https://pkg.jenkins.io/debian/"
    assert repo.dist == "binary"
    assert repo.components == []

def test_flat_repo_packages():
    flat_repo.packages

def test_flat_repo_get_binary_packages_by_component():
    flat_repo.get_binary_packages_by_component(None)

def test_flat_repo_get_packages_by_name():
    flat_repo.get_packages_by_name("jenkins")

def test_flat_repo_get_package():
    version = flat_repo.get_packages_by_name("jenkins")[0].version
    flat_repo.get_package("jenkins", version)

def test_flat_repo_get_package_url():
    version = flat_repo.get_packages_by_name("jenkins")[0].version
    flat_repo.get_package_url("jenkins", version)
